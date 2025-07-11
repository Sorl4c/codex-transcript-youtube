import re

def is_url(string: str) -> bool:
    """Checks if a string is a valid URL."""
    # Regex simple para detectar si parece una URL
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// o https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...o ip
        r'(?::\d+)?'  # puerto opcional
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE)
    return re.match(regex, string) is not None
