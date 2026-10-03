import logging
from abc import ABC
from typing import Any

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
POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
    {"id": 3, "title": "Third post", "content": "This is the third post."},
    {"id": 4, "title": "Fourth post", "content": "This is the fourth post."},
    {"id": 5, "title": "Fifth post", "content": "This is the fifth post."},
    {"id": 6, "title": "Sixth post", "content": "This is the sixth post."},
    {"id": 7, "title": "Seventh post", "content": "This is the seventh post."},
    {"id": 8, "title": "Eighth post", "content": "This is the eighth post."},
    {"id": 9, "title": "Ninth post", "content": "This is the ninth post."},
    {"id": 10, "title": "Tenth post", "content": "This is the tenth post."},
    {"id": 11, "title": "Eleventh post", "content": "This is the eleventh post."},
    {"id": 12, "title": "Twelfth post", "content": "This is the twelfth post."},
    {"id": 13, "title": "Thirteenth post", "content": "This is the thirteenth post."},
    {"id": 14, "title": "Fourteenth post", "content": "This is the fourteenth post."},
    {"id": 15, "title": "Fifteenth post", "content": "This is the fifteenth post."},
]
STRING = str
NUMBER = int
POST_ATTR_CFG = {
    "title": {"type": STRING, "min": 1, "required": True, "label": "Title"},
    "content": {"type": STRING, "min": 1, "required": True, "label": "Content"},
    "id": {"type": NUMBER, "edible": False, "label": "ID"},
}


def read_data():
    # TODO: read JSON file
    return POSTS


def insert(new_post: dict) -> None:
    """
    Insert a new record in the posts list.

    Args:
        - new_post: New post
    """
    POSTS.append(new_post)


def remove(post: dict) -> None:
    """
    Remove a post from the posts list.

    Args:
        - post: Post to be deleted
    """
    POSTS.remove(post)


def get_all_posts() -> list:
    """
    Get all existente posts of the blog.


    Returns:
        A list of posts.
    """
    posts = read_data()
    if posts:
        return posts
    return []


def get_post_by_id(post_id: int) -> dict | None:
    """
    Fetch in the data a post with the given id number.

    Args:
        post_id: ID number.

    Returns:
        Post found or None.


    """
    try:
        blog_posts = read_data()

        return next((post for post in blog_posts if post["id"] == int(post_id)), None)

    except Exception as e:
        raise ValueError(f"Error fetching post by ID. Error: {e}")


def next_id() -> int:
    """
    Return next unique ID for blog db.

    Returns:
        id: next ID
    """
    # getting last ID number from posts list
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
        }

        insert(new_post)

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
        String with the missing or invalid inputs.
        False for No attributte missing or invalid.
    """

    error_messsage = ""
    invalid_fields = []

    # validate user input
    for update in user_input.keys():
        if update in POST_ATTR_CFG and POST_ATTR_CFG[update].get(
            "edible", True
        ):  # check post dictionary settings
            field_cfg = POST_ATTR_CFG[update]
            if type(update) is not field_cfg["type"]:
                error_messsage += (
                    f"{field_cfg['label']} provided is not {field_cfg['type']}."
                )
            elif (
                field_cfg.get("min", None)
                and len(user_input[update].strip()) < field_cfg["min"]
            ):
                error_messsage += f"{field_cfg['label']} provided is invalid. "
        else:
            logger.debug("Invalid input %s removed from updates.", update)
            invalid_fields.append(update)

    for field in invalid_fields:
        user_input.pop(field)

    if not user_input:
        error_messsage = "No valid updates provided."

    if not error_messsage:
        return True, None
    return False, error_messsage


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

        for update in user_input.keys():
            post[update] = user_input[update]

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
    for post in POSTS:
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
    if POST_ATTR_CFG[term]["type"] == STRING:
        value_edt = value.casefold().strip()
        post_value_edt = post[term].casefold().strip()
        return post_value_edt.find(value_edt) >= 0

    if POST_ATTR_CFG[term]["type"] == NUMBER and value.isnumeric():
        return post[term] == int(value)

    return post[term] == value
