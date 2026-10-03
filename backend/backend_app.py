import logging

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

import blog

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Setting API docs
SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Masterblog API"},
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@app.route("/api/posts", methods=["GET"])
def get_posts():
    """
    Operation: List
    Args:
        Optional: query parameters with sorting terms.

    Returns:
        - Success: ‘200’, list with all posts.

    """
    if request.args:
        sort_by = request.args.get("sort", None)
        if sort_by and sort_by in blog.POST_ATTR_CFG:
            direction = request.args.get("direction", "asc").strip().casefold()
            if direction not in ["desc", "asc"]:
                direction = "asc"
            return jsonify(blog.get_all_posts(sort_args=(sort_by, direction == "desc")))

    return jsonify(blog.get_all_posts())


@app.route("/api/posts", methods=["POST"])
def add():
    """
    Post Method:
    Create a new post.

    Args:
        post: Post data to create.

    Returns:
        - Success: ‘201’, complete created post including ID.
        - Failure/edge case:
            - Missing and blank required fields:
                        ‘400’,  {”error”: “Missing required field: <field_name>”}.
            - Wrongly typed fields:
                         ‘400’,  {”error”: “Failed validation description”}.
    """

    # Method POST
    logger.debug("Read payload")
    user_input = request.get_json(silent=True)
    logger.debug("Validate payload")
    missing_input = validate_input(user_input)

    if missing_input:
        return jsonify({"error": missing_input}), 400

    # create a new post
    logger.debug("Create a new post.")
    response = blog.create_post(user_input)
    if response.status:
        return jsonify(response.result), 201

    return jsonify(response.error), response.error["code"]


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """
    Delete a post.

    Args:
        id: Post id to be deleted.

    Returns:
        Success: 200, {"message": "Post with id <id> has been deleted successfully."}

        Post not found: 404, {”error”: “Post not found.”}
    """

    if int(post_id) == 0:
        return {"message": "Invalid post id provided."}, 400

    response = blog.delete_post(post_id)
    if response.status:
        return jsonify(response.result), 200

    return jsonify(response.error), response.error["code"]


@app.route("/api/posts/<int:post_id>", methods=["PATCH"])
def update(post_id):
    """
    Update a post.

    Args:
        id: Post id to be updated.
        body: Fields to be updated. Omitted fields are not changed.

    Returns:
        Success: ‘200’, updated  stored post dictionary
        Post not found:  ‘404’, {”error”: “Post not found.”}
        Invalid ID:  ‘400’, {”error”: “Invalid post ID number provided.}
        No input provided: ‘400’, {”error”: “No updates provided.”}
        Invalid input: ‘400’, {”error”: “Failed validation description”}
    """

    if int(post_id) == 0:
        return {"error": "Invalid post ID number provided."}, 400

    user_input = request.get_json(silent=True)

    if not user_input or len(user_input) == 0:
        return {"error": "No updates provided."}, 400

    response = blog.update_post(user_input, post_id)

    if response.status:
        return jsonify(response.result), 200

    return jsonify(response.error), response.error["code"]


@app.route("/api/posts/search")
def search():
    """
    Operation: Search
    Args:
        Optional: query parameters with search criteria

    Returns:
        Success: ‘200’, list matched posts
        No match:  ‘200’, []
        None and blank or invalid search term: ‘400’,
            {”error”: “Search term or value invalid.”}

    """
    if not request.args:
        return {"error": "No search criteria provided."}, 400

    logger.debug(request.args)

    response = blog.filter_posts(request.args)

    if response.status:
        return jsonify(response.result), 200

    return jsonify(response.error), response.error["code"]


def validate_input(user_input: dict) -> str | bool:
    """
    Validate fields type, valid content, and required attributtes.

    Args:
        post: Post data.

    Returns:
        String with the missing or invalid inputs.
        False for No attributte missing or invalid.
    """

    if not user_input:
        return "Invalid request."

    error_message = ""
    for field, settings in blog.POST_ATTR_CFG.items():
        field_value = str(user_input.get(field, "")).strip()
        if field_value:
            if settings["type"] == blog.date:
                if not blog.parse_date(user_input[field]):
                    error_message += "Date provided is invalid."
            elif type(user_input[field]) is not settings["type"]:
                error_message += f"Field {field} expected: {settings['type']} received: {type(user_input[field])}. "

                logger.info(error_message)
            elif len(field_value) < settings.get("min", -1):
                error_message += f"Invalid value provided for {field}. "

        elif settings.get("required", False):
            error_message += f"Required field not provided: {field}. "

    return error_message


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
