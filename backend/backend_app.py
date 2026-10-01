import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

import blog

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = app.logger


@app.route("/api/posts", methods=["GET"])
def get_posts():
    """
    Operation: List
    Args:
        Optional: query parameters with sorting terms.

    Returns:
        - Success: ‘200’, list with all posts.

    """
    return jsonify(blog.POSTS)


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
    user_input = request.get_json()
    logger.debug("Validate payload")
    missing_input = validate_input(user_input)

    if missing_input:
        return {"error": missing_input}, 400

    # create a new post
    logger.debug("Create a new post.")
    response = blog.create_post(user_input)
    if response.status:
        return jsonify(response.result), 201

    return response.error, response.error["code"]


def validate_input(user_input: dict) -> str | bool:
    """
    Validate fields type, valid content, and required attributtes.

    Args:
        post: Post data.

    Returns:
        String with the missing or invalid inputs.
        False for No attributte missing or invalid.
    """
    if user_input:
        required_input = ["title", "content"]
        input_not_found = next(
            (
                field
                for field in required_input
                if field not in user_input
                or not isinstance(user_input[field], str)
                or not user_input[field].strip()
            ),
            None,
        )
    else:
        input_not_found = "all"

    if input_not_found is not None:
        logger.debug(f"Missing fields: {input_not_found}")
        return f"Please provide all required fields. Missing: {input_not_found}"

    return False


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
