from fastapi import FastAPI, Request

from .translator import Translator


def apply_translation(app: FastAPI, translator: Translator) -> None:
    """Register middleware for accessing request locale."""

    @app.middleware("http")
    async def set_locale_context(request: Request, call_next):
        header = request.headers.get("accept-language")
        locale = header.split(",") if header else None
        if locale:
            for entry in locale:
                lang = entry.split(";")
                if lang[0] in translator.get_languages():
                    translator.set_active_language(str(lang[0]))
                    break
        return await call_next(request)
