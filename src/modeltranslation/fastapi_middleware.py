from fastapi import FastAPI, Request

from .translator import Translator


def apply_translation(app: FastAPI, translator: Translator) -> None:
    """Configure the app set the current language as a context variable.

    Applies middleware to FastAPI app which sets language based on the accept-language HTTP header.
    The resolved language is stored in the translator per execution context.

    Args:
        app (FastAPI): FastAPI application.
        translator (Translator): The translator used to register translations in this app.

    Examples:
        >>> translator = Translator(
        ...     default_language="en",
        ...     languages=("en", "pl"),
        ... )
        >>> app = FastAPI()
        >>> apply_translation(app, translator)

    """

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
