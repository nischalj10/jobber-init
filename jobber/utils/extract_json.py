import json
import re


def extract_json(text: str) -> dict:
    """
    Extracts JSON content from a given string, supporting deeply nested objects
    and handling escaped braces in strings.

    Args:
        text (str): The input string containing JSON data.

    Returns:
        dict: The extracted JSON data as a Python dictionary.

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
    """
    Extracts JSON content from a given string, supporting deeply nested objects.

    Args:
        text (str): The input string containing JSON data.

    Returns:
        dict: The extracted JSON data as a Python dictionary.

    Raises:
        ValueError: If no valid JSON is found in the input string.
    """
    # Find all opening and closing braces
    opens = [m.start() for m in re.finditer("{", text)]
    closes = [m.start() for m in re.finditer("}", text)]

    if not opens or not closes:
        raise ValueError("No valid JSON found in the input string")

    # Find the outermost JSON object
    stack = []
    for i, open_pos in enumerate(opens):
        stack.append(open_pos)
        while closes and closes[0] < open_pos:
            closes.pop(0)
        if closes and (
            not stack or closes[0] < opens[i + 1] if i + 1 < len(opens) else True
        ):
            close_pos = closes.pop(0)
            start = stack.pop(0)
            if not stack:
                # This is the outermost object
                json_str = text[start : close_pos + 1]
                break
    else:
        raise ValueError("No valid JSON found in the input string")

    # Use regex to remove any non-JSON content
    json_str = re.sub(r"[^\x20-\x7E]", "", json_str)

    try:
        # Parse the JSON string into a Python dictionary
        json_data = json.loads(json_str)
        return json_data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format in the extracted content")
