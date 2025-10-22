def add(x: int, y: int) -> int:
    """Test docstring.

    This is a dummy docstring used to test ruff and mkdocstrings.

    Args:
        x (int): first number
        y (int): second number

    Returns:
        int: the sum of x and y.

    Raises:
        ValueError: This is here to supress a warning.

    Examples:
        >>> add(1, 2)
        3

    """
    return x + y
