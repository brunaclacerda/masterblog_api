import logging
import operator
from abc import ABC
from datetime import date
from typing import Any

import data.data as db

logger = logging.getLogger(__name__)


class BlogResponse(ABC):
    """
    Interface Class for responses for operation related to the blog.

    Constructor:
        status: Status of the operation.
        error: message and error code

    """

    def __init__(self, status: bool, error: dict | None = None):
        self.status = status
        self.error = error


class BlogSuccessResponse(BlogResponse):
    """
    Class for standard response for successful operation.

    """

    def __init__(self, result: Any = None):
        super().__init__(SUCCESS)
        self.result = result


class BlogFailedResponse(BlogResponse):
    """
    Interface Class for responses for operation related to the blog.

    Constructor:
        status: Status of the operation.
        error: message and error code

    """

    def __init__(self, error: dict):
        super().__init__(FAILED, error)


SUCCESS = True
FAILED = False
NOT_FOUND = False
POST_ATTR_CFG = {
    "title": {"type": str, "min": 1, "required": True, "label": "Title"},
    "content": {"type": str, "min": 1, "required": True, "label": "Content"},
    "id": {"type": int, "edible": False, "label": "ID"},
    "author": {"type": str, "min": 1, "label": "Author"},
    "date": {"type": date, "label": "Creation date"},
}


def insert(new_post: dict) -> None:
    """
    Insert a new record in the posts list.

    Args:
        - new_post: New post
    """
    posts = db.read_data()
    posts.append(new_post)
    db.update_data(posts)


def remove(post: dict) -> None:
    """
    Remove a post from the posts list.

    Args:
        - post: Post to be deleted
    """
    posts = db.read_data()
    posts.remove(post)
    db.update_data(posts)


def update_data(post_updated: dict) -> None:
    """
    Update a post on the posts list.

    Args:
        - post: Post to be deleted
    """
    posts = db.read_data()
    post_to_update = next(
        (post for post in posts if post["id"] == int(post_updated["id"])), None
    )
    # for field, settings in POST_ATTR_CFG.items():
    #     if settings.get("edible", True):
    #         post_to_update[field] = post_updated[field]

    post_to_update.update(post_updated)
    db.update_data(posts)


def get_all_posts(sort_args: tuple[str, bool] | None = None) -> list:
    """
    Get all existente posts of the blog.


    Returns:
        A list of posts.
    """
    posts = db.read_data()
    if posts:
        if sort_args:
            logger.debug("Sorting list by: %s", sort_args)
            if POST_ATTR_CFG[sort_args[0]]["type"] == date:
                return sorted(
                    posts,
                    key=lambda post, col=sort_args[0]: parse_date(post[col]),
                    reverse=sort_args[1],
                )
            sorted_posts = sorted(
                posts, key=operator.itemgetter(sort_args[0]), reverse=sort_args[1]
            )
            return sorted_posts
        return posts
    return []


def get_post_by_id(post_id: int) -> dict | None:
    """
    Fetch in the data a post with the given id int.

    Args:
        post_id: ID int.

    Returns:
        Post found or None.


    """
    try:
        blog_posts = db.read_data()

        return next((post for post in blog_posts if post["id"] == int(post_id)), None)

    except Exception as e:
        raise ValueError(f"Error fetching post by ID. Error: {e}")


def next_id() -> int:
    """
    Return next unique ID for blog db.

    Returns:
        id: next ID
    """
    # getting last ID int from posts list
    last_id = max((post["id"] for post in get_all_posts()), default=0)
    return last_id + 1


def create_post(user_input: dict) -> BlogResponse:
    """
    Create a post.

    Args:
        user_input: Form-data provided by the user.

    Returns:
        response.status: Status of data insertion.
            True for successful operation and False for failed.
        response.error: None or error object. Error only if status is False
    """
    try:
        new_post = {
            "id": next_id(),
            "title": user_input["title"],
            "content": user_input["content"],
            "author": user_input.get("author", None),
            "date": user_input.get("date", None),
        }

        insert(new_post)
        logger.debug(new_post)

        return BlogSuccessResponse(new_post)

    except Exception as e:
        logger.error("Error creating a post: %s", e)
        return BlogFailedResponse({"error": "Unexpected error.", "code": 500})


def delete_post(post_id: int) -> BlogResponse:
    """
    Delete post with the provided id.

    Args:
        post_id: Post unique id.

    Returns:
        status: True for successful operation and False for failed.
        result: Operation result if status True
        error: error dictionary if status is False
    """
    try:
        post = get_post_by_id(post_id)
        if not post:
            return BlogFailedResponse({"message": "Post not found.", "code": 404})

        remove(post)
        return BlogSuccessResponse(
            {"message": f"Post with id {post_id} has been deleted successfully."}
        )

    except Exception as e:
        logger.error("Error deleting post %s: %s", post_id, e)
        return BlogFailedResponse({"message": "Unexpected error.", "code": 500})


def validate_upt(user_input: dict) -> tuple[bool, str | None]:
    """
    Validate fields type, valid content, and required attributtes.

    Args:
        post: Post data.

    Returns:
        str with the missing or invalid inputs.
        False for No attributte missing or invalid.
    """

    error_message = ""
    invalid_fields = []

    # validate user input
    for update, value in user_input.items():
        if update in POST_ATTR_CFG and POST_ATTR_CFG[update].get(
            "edible", True
        ):  # check post dictionary settings
            field_cfg = POST_ATTR_CFG[update]
            if field_cfg["type"] == date:
                if not parse_date(value):
                    error_message += "Date provided is invalid."
            elif type(value) is not field_cfg["type"]:
                error_message += (
                    f"{field_cfg['label']} provided is not {field_cfg['type']}."
                )
            elif field_cfg.get("min", -1) > len(value.strip()):
                error_message += f"{field_cfg['label']} provided is invalid. "

        else:
            logger.debug("Invalid input %s removed from updates.", update)
            invalid_fields.append(update)

    for field in invalid_fields:
        user_input.pop(field)

    if not user_input:
        error_message = "No valid updates provided."

    if not error_message:
        return True, None
    return False, error_message


def parse_date(value: str) -> date | None:
    """
    Parse value to a ISO date.
    """
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as e:
        logger.error("Error parsing date: %s", e)
        return None


def update_post(user_input: dict, post_id: int) -> BlogResponse:
    """
    Update a post with the provided id.

    Args:
        user_input: Dictionary with the updates
        post_id: Post unique id.

    Returns:
        status: True for successful operation and False for failed.
        result: Operation result if status True
        error: error dictionary if status is False
    """

    try:
        is_valid, error = validate_upt(user_input)
        if not is_valid:
            return BlogFailedResponse({"error": error, "code": 400})

        post = get_post_by_id(post_id)
        if not post:
            return BlogFailedResponse({"error": "Post not found.", "code": 404})

        for update in user_input:
            post[update] = user_input[update]

        update_data(post)
        return BlogSuccessResponse(post)

    except Exception as e:
        print(e)
        return BlogFailedResponse({"error": "Unexpected error.", "code": 500})


def filter_posts(filters: dict) -> BlogResponse:
    """
    Get posts list that match with user search criteria.


    Returns:
        status: True for successful operation and False for failed.
        result: Operation result if status True
        error: error dictionary if status is False
    """

    invalid_filters = next(
        (
            term
            for term, value in filters.items()
            if term not in POST_ATTR_CFG
            or (isinstance(value, str) and value.strip() == "")
        ),
        None,
    )

    if invalid_filters:
        return BlogFailedResponse(
            {"error": "Search term or value invalid.", "code": 400}
        )

    filtered_posts = []
    posts = get_all_posts()
    for post in posts:
        match = all(
            check_filter(filter, value, post) for filter, value in filters.items()
        )
        if match:
            filtered_posts.append(post)

    return BlogSuccessResponse(filtered_posts)


def check_filter(term: str, value: str, post: dict) -> bool:
    """
    Helper function to check if post matches all search term
    """
    if POST_ATTR_CFG[term]["type"] == str:
        value_edt = value.casefold().strip()
        post_value_edt = post[term].casefold().strip()
        return post_value_edt.find(value_edt) >= 0

    if POST_ATTR_CFG[term]["type"] == int and value.isnumeric():
        return post[term] == int(value)

    return post[term] == value
