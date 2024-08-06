import json
from typing import Dict


def extract_json(text: str) -> Dict:
    """
    Extracts JSON content from a given string, supporting deeply nested objects
    and handling escaped braces in strings.

    Args:
        text (str): The input string containing JSON data.

    Returns:
        Dict: The extracted JSON data as a Python dictionary.

    Raises:
        ValueError: If no valid JSON is found in the input string.
    """
    stack = []
    start = -1
    in_string = False
    escape = False

    for i, char in enumerate(text):
        if char == '"' and not escape:
            in_string = not in_string
        elif char == "\\" and in_string:
            escape = not escape
            continue
        elif char == "{" and not in_string:
            if not stack:
                start = i
            stack.append(i)
        elif char == "}" and not in_string:
            if stack:
                stack.pop()
                if not stack:
                    # This is the outermost object
                    json_str = text[start : i + 1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        # If parsing fails, continue searching
                        continue

        escape = False  # Reset escape flag after each character

    raise ValueError("No valid JSON found in the input string")
