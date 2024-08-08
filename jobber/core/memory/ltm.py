import os

from jobber.config import USER_PREFERENCES_PATH
from jobber.utils.logger import logger


def get_ltm():
    """
    Get the user preferences from user_preference.txt file.
    returns: str | None - The uder preferences stored in the user_preference.txt file or None if the file does not exist.
    """
    user_preference_file_name = "user_preferences.txt"
    user_preference_file = os.path.join(
        USER_PREFERENCES_PATH, user_preference_file_name
    )
    try:
        with open(user_preference_file) as file:
            user_pref = file.read()
        logger.info(f"User preferences loaded from: {user_preference_file}")
        return user_pref
    except FileNotFoundError:
        logger.warning(f"User preference file not found: {user_preference_file}")

    return None 
