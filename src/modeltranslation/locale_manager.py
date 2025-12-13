from fastapi import FastAPI, Request

from .translator import Translator


def apply_translation(app: FastAPI) -> None:
    """Register middleware for accessing request locale."""

    @app.middleware("http")
    async def set_locale_context(request: Request, call_next):
        header = request.headers.get("accept-language")
        locale = header.split(",")[0].strip() if header else None

        Translator.set_locale(locale)
        return await call_next(request)
