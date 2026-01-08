from collections.abc import Callable, Iterator
from contextvars import ContextVar
from copy import deepcopy
from functools import wraps

from sqlalchemy import Column
from sqlalchemy.orm import column_property
from sqlmodel import SQLModel


class TranslationOptions:
    fields: tuple[str] = ()
    fallback_languages: dict[str, tuple[str]] = None
    fallback_values: dict[str, any] | any = None
    fallback_undefined: dict[str, any] = None
    required_languages: dict[str, tuple[str]] | tuple[str] = None


class Translator:
    def __init__(
            self,
            default_language: str,
            languages: tuple[str],
            fallback_languages: dict[str, tuple[str]] | None = None
        ) -> None:

        self._active_language: ContextVar[str] = ContextVar("current_locale", default=default_language)

        # default language
        self._default_language: str = default_language

        # supported languages
        self._languages: tuple[str] = languages

        # fallbacks for untranslated languages
        self._fallback_languages: dict[str, tuple[str]] = {"default": (self._default_language,)}
        if fallback_languages:
            self._fallback_languages = fallback_languages

    def get_active_language(self) -> str:
        return self._current_language.get()

    def set_active_language(self, locale: str) -> None:
        self._current_locale.set(locale)

    def get_default_language(self) -> str:
        return self._default_language

    def register(self, model: type[SQLModel]) -> Callable:
        def decorator(options: type[TranslationOptions]) -> None:
            self._replace_accessors(model, options)
            self._rebuild_model(model, options)

        return decorator

    def _replace_accessors(
        self, model: type[SQLModel], translation_options: TranslationOptions
    ) -> type[SQLModel]:
        def locale_get_decorator(original_get_function: Callable) -> Callable:
            @wraps(original_get_function)
            def locale_function(model_self: SQLModel, name: str, *args: any) -> any:
                # ignore private and not translated functions
                if name.startswith("_") or name not in translation_options.fields:
                    return original_get_function(model_self, name, *args)

                current_locale = self.get_locale()

                if current_locale in self._languages:
                    value = original_get_function(model_self, f"{name}_{current_locale}")
                    if not self._is_null_value(name, value, translation_options):
                        return value

                for fallback_language in self._fallbacks_generator(current_locale, translation_options):
                    value = original_get_function(model_self, f"{name}_{fallback_language}")
                    if not self._is_null_value(name, value, translation_options):
                        return value

                # no fallback language yielded a value, try fallback values
                return self._fallback_value(name, translation_options)

            return locale_function

        def locale_set_decorator(original_set_function: Callable) -> Callable:
            @wraps(original_set_function)
            def locale_function(model_self: SQLModel, name: str, value: any) -> None:
                # ignore private and not translated functions
                if name.startswith("_") or name not in translation_options.fields:
                    return original_set_function(model_self, name, value)

                current_locale = self.get_locale()
                # if language is in translation use it, else use the default translator language
                if current_locale in self._languages:
                    return original_set_function(model_self, f"{name}_{current_locale}", value)
                return original_set_function(model_self, f"{name}_{self._default_language}", value)

            return locale_function

        model.__class__.__getattribute__ = locale_get_decorator(model.__class__.__getattribute__)
        model.__getattribute__ = locale_get_decorator(model.__getattribute__)
        model.__setattr__ = locale_set_decorator(model.__setattr__)
        return model

    def _rebuild_model(self, model: type[SQLModel], translation_options: TranslationOptions) -> None:
        for field in translation_options.fields:
            for lang in translation_options.languages:
                field_name = f"{field}_{lang}"

                orig_type = model.__table__.columns[field].type

                column = Column(field_name, orig_type, nullable=True)
                model.__table__.append_column(column)

                pydantic_field = deepcopy(model.model_fields[field])
                pydantic_field.alias = field_name
                model.model_fields[field_name] = pydantic_field

                orig_annotation = model.__annotations__[field]

                model.__annotations__[field_name] = orig_annotation

                setattr(model, field_name, column_property(column))

        model.model_rebuild(force=True)

    def _is_required_language(self, language: str, field: str, options: TranslationOptions) -> bool:
        if type(options) is tuple:
            return language in options
        if language in options.required_languages:
            return field in options[language]
        if "default" in options.required_languages:
            return field in options["default"]
        return False

    def _is_null_value(self, field: str, value: any, options: TranslationOptions) -> bool:
        # if translation defines custom fallback undefined value then check if value is eq to it
        if options.fallback_undefined is not None and field in options.fallback_undefined:
            return value == options.fallback_undefined[field]
        # else check if value is eq None
        return value is None

    def _fallbacks_generator(self, language: str, options: TranslationOptions) -> Iterator[str]:
        if options.fallback_languages is not None:
            yield from self._yield_fallbacks(language, options.fallback_languages)
        elif self._fallback_languages is not None:
            yield from self._yield_fallbacks(language, self._fallback_languages)

    def _yield_fallbacks(self, language: str, fallbacks: dict[str, tuple[str]] | None) -> Iterator[str]:
        if not fallbacks:
            return

        if language in fallbacks:
            candidates = fallbacks[language]
        elif "default" in fallbacks:
            candidates = fallbacks["default"]
        else:
            return

        for fallback in candidates:
            if fallback != language:
                yield fallback

    def _fallback_value(self, field: str, options: TranslationOptions) -> any:
        if options.fallback_values is None:
            return None
        if type(options.fallback_languages) is not dict:
            return options.fallback_values
        if field in options.fallback_values:
            return options.fallback_values[field]
        return None
