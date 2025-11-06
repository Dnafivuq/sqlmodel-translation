from fastapi import FastAPI, Request
from contextvars import ContextVar


current_locale: ContextVar[str] = ContextVar("current_locale", default="en")


def register_app(app: FastAPI):
    """Register middleware for accessing request locale"""

    @app.middleware("http")
    async def set_locale_context(request: Request, call_next):
        header = request.headers.get("accept-language")
        if header:
            locale = header.split(",")[0].strip()
        else:
            locale = None

        current_locale.set(locale)
        response = await call_next(request)
        return response
