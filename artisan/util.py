__all__ = [
    "convert_to_string"
]


def convert_to_string(string):
    if isinstance(string, bytes):
        return string.decode("utf-8")
    return string
