"""Module fol helper functions."""


def dict_helper(objects: list) -> list[dict]:
    """Parse database query return value.

    Takes database records returned by query as list of objects and parse them
    to list of dictionaries. Dictionary is generated according to class method to_dict().

    Args:
        objects: List of objects.

    Returns:
        List of dictionaries.
    """
    result = [item.to_dict() for item in objects]
    return result
