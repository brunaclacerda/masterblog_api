import logging
import operator
from abc import ABC
from typing import Any
from datetime import date

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
    {
        "id": 1,
        "title": "A Better Morning Protocol",
        "content": "Pepper says coffee is not a food group. I disagree, but I also installed a hydration reminder in the armor. Progress means listening to good advice, even when it arrives before the first espresso.",
        "author": "Tony Stark",
        "date": "2026-09-18",
    },
    {
        "id": 2,
        "title": "The Shield Is Not a Shortcut",
        "content": "Training with the shield teaches the same lesson every time: momentum matters, but control matters more. Take the time to learn the return path before you throw yourself into the fight.",
        "author": "Steve Rogers",
        "date": "2026-09-20",
    },
    {
        "id": 3,
        "title": "Three Ways to Spot a Bad Deal",
        "content": "If someone offers you everything you want with no questions asked, ask more questions. If they call you family after five minutes, leave. If the room has red lighting, definitely leave.",
        "author": "Natasha Romanoff",
        "date": "2026-09-22",
    },
    {
        "id": 4,
        "title": "Storm-Watching From New Asgard",
        "content": "A storm is not merely a warning. It is a conversation between sky and sea, reminding us that strength without purpose is only noise. Also, the goats remain forbidden from the roof.",
        "author": "Thor Odinson",
        "date": "2026-09-24",
    },
    {
        "id": 5,
        "title": "The Science of Taking a Breath",
        "content": "When the problem gets bigger, my first instinct is to get bigger too. The better answer is often to pause, breathe, and make sure I am fighting the problem instead of everyone standing near it.",
        "author": "Bruce Banner",
        "date": "2026-09-26",
    },
    {
        "id": 6,
        "title": "Clint's Extremely Practical Picnic Guide",
        "content": "Pack sandwiches. Bring a blanket. Do not invite anyone carrying experimental arrows. And if Scott says he can make the cooler bigger on the inside, politely say no.",
        "author": "Clint Barton",
        "date": "2026-09-28",
    },
    {
        "id": 7,
        "title": "Wakanda's Quiet Innovation",
        "content": "Technology should serve people before it impresses them. The most meaningful advances are the ones that make a village safer, a journey easier, or a child more curious about tomorrow.",
        "author": "Shuri",
        "date": "2026-09-30",
    },
    {
        "id": 8,
        "title": "Friendly Neighborhood Field Notes",
        "content": "Today's patrol results: returned one lost dog, helped three tourists find the subway, and prevented a bicycle theft. No cosmic disasters, which feels like a win. Also, please wear helmets.",
        "author": "Peter Parker",
        "date": "2026-10-01",
    },
    {
        "id": 9,
        "title": "On Choosing the Hard Right",
        "content": "Power means little if it only protects what is convenient. We honor those who came before us by choosing compassion when it costs us something.",
        "author": "Sam Wilson",
        "date": "2026-10-02",
    },
    {
        "id": 10,
        "title": "A Small Practice in Magic",
        "content": "Before attempting a new spell, make tea and clear your mind. An untidy room can be repaired; an untidy dimension is considerably more difficult to explain to the neighbors.",
        "author": "Doctor Stephen Strange",
        "date": "2026-10-03",
    },
]
POST_ATTR_CFG = {
    "title": {"type": str, "min": 1, "required": True, "label": "Title"},
    "content": {"type": str, "min": 1, "required": True, "label": "Content"},
    "id": {"type": int, "edible": False, "label": "ID"},
    "author": {"type": str, "min": 1, "label": "Author"},
    "date": {"type": date, "label": "Creation date"},
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


def get_all_posts(sort_args: tuple[str, bool] | None = None) -> list:
    """
    Get all existente posts of the blog.


    Returns:
        A list of posts.
    """
    posts = read_data()
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
    if POST_ATTR_CFG[term]["type"] == str:
        value_edt = value.casefold().strip()
        post_value_edt = post[term].casefold().strip()
        return post_value_edt.find(value_edt) >= 0

    if POST_ATTR_CFG[term]["type"] == int and value.isnumeric():
        return post[term] == int(value)

    return post[term] == value
