__all__ = ["Context"]

class Context:
    """Minimal Context SDK facade.

    Example:
        >>> from context_sdk import Context
        >>> ctx = Context()
        >>> ctx.echo("hello")
        'hello'
    """

    def echo(self, message: str) -> str:
        if not isinstance(message, str):
            raise TypeError("message must be a string")
        return message


