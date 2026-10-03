import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE_PATH = BASE_DIR / "posts.json"


def read_data():
    """
    Load the JSON file.

    Returns:
        List of the JSON file content.
    """
    try:
        with open(DATA_FILE_PATH) as file:
            json_file = json.load(file)
            return json_file
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")

        return None


def update_data(data):
    """
    Replace the data JSON file.

    Args:
        data: List of the posts to be saved.

    """
    try:
        with open(DATA_FILE_PATH, "w") as file:
            content = json.dumps(data)
            file.write(content)
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        raise
