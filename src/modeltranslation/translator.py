from collections.abc import Callable, Iterator
from contextvars import ContextVar
from copy import deepcopy
from functools import wraps
from typing import Any, Union, get_args, get_origin

from sqlalchemy import Column
from sqlalchemy.orm import column_property
from sqlmodel import SQLModel


class TranslationOptions:
    fields: tuple[str, ...] = ()
    fallback_languages: dict[str, tuple[str, ...]] | None = None
    fallback_values: dict[str, Any] | Any = None
    fallback_undefined: dict[str, Any] | None = None
    required_languages: dict[str, tuple[str, ...]] | tuple[str, ...] | None = None


class Translator:
    def __init__(
        self,
        default_language: str,
        languages: tuple[str, ...],
        fallback_languages: dict[str, tuple[str, ...]] | None = None,
    ) -> None:
        self._active_language: ContextVar[str] = ContextVar("current_locale", default=default_language)

        # default language
        self._default_language: str = default_language

        # supported languages
        self._languages: tuple[str, ...] = languages

        # fallbacks for untranslated languages
        self._fallback_languages: dict[str, tuple[str, ...]] = {"default": (self._default_language,)}
        if fallback_languages:
            self._fallback_languages = fallback_languages

    def get_languages(self) -> tuple[str]:
        return self._languages

    def get_active_language(self) -> str:
        return self._active_language.get()

    def set_active_language(self, locale: str) -> None:
        self._active_language.set(locale)

    def get_default_language(self) -> str:
        return self._default_language

    def register(self, model: type[SQLModel]) -> Callable:
        def decorator(options: TranslationOptions) -> None:
            self._replace_accessors(model, options)
            self._rebuild_model(model, options)

        return decorator

    def _replace_accessors(  # noqa: C901
        self, model: type[SQLModel], options: TranslationOptions
    ) -> type[SQLModel]:
        def locale_get_decorator(original_get_function: Callable) -> Callable:
            @wraps(original_get_function)
            def locale_function(
                model_self: type[SQLModel] | SQLModel, name: str, *args: tuple[Any, ...]
            ) -> Callable:
                # ignore private and not translated functions
                if name.startswith("_") or name not in options.fields:
                    return original_get_function(model_self, name, *args)

                active_language = self.get_active_language()

                if active_language in self._languages:
                    value = original_get_function(model_self, f"{name}_{active_language}")
                    if not self._is_null_value(name, value, options):
                        return value

                for fallback_language in self._fallbacks_generator(active_language, options):
                    value = original_get_function(model_self, f"{name}_{fallback_language}")
                    if not self._is_null_value(name, value, options):
                        return value

                # no fallback language yielded a value, try fallback values
                return self._fallback_value(name, options)

            return locale_function

        def locale_set_decorator(original_set_function: Callable) -> Callable:
            @wraps(original_set_function)
            def locale_function(model_self: type[SQLModel], name: str, value: Any) -> Callable:
                # ignore private and not translated functions
                if name.startswith("_") or name not in options.fields:
                    return original_set_function(model_self, name, value)

                active_language = self.get_active_language()
                # if language is in translation use it, else use the default translator language
                if active_language in self._languages:
                    return original_set_function(model_self, f"{name}_{active_language}", value)
                return original_set_function(model_self, f"{name}_{self._default_language}", value)

            return locale_function

        def locale_class_get_decorator(original_get_function: Callable) -> Callable:
            @wraps(original_get_function)
            def locale_function(
                model_self: type[SQLModel] | SQLModel, name: str, *args: tuple[Any, ...]
            ) -> Callable:
                # ignore private and not translated functions
                if name.startswith("_") or name not in options.fields:
                    return original_get_function(model_self, name, *args)

                active_language = self.get_active_language()

                if active_language in self._languages:
                    return original_get_function(model_self, f"{name}_{active_language}")

                for fallback_language in self._fallbacks_generator(active_language, options):
                    return original_get_function(model_self, f"{name}_{fallback_language}")

                return original_get_function(model_self, f"{name}_{self._default_language}")

            return locale_function

        model.__class__.__getattribute__ = locale_class_get_decorator(model.__class__.__getattribute__)
        model.__getattribute__ = locale_get_decorator(model.__getattribute__)
        model.__setattr__ = locale_set_decorator(model.__setattr__)
        return model

    def _rebuild_model(self, model: type[SQLModel], options: TranslationOptions) -> None:
        for field in options.fields:
            orig_type = model.__table__.columns[field].type
            orig_annotation = model.__annotations__[field]

            # change field to be Nullable
            model.__table__.columns[field].nullable = True
            model.__annotations__[field] = self._make_optional(orig_annotation)
            model.model_fields[field].annotation = model.__annotations__[field]

            for lang in self._languages:
                translation_field = f"{field}_{lang}"

                translation_annotation = (
                    orig_annotation
                    if self._is_required(lang, field, options)
                    else self._make_optional(orig_annotation)
                )

                # change model SQL Alchemy table
                column = Column(
                    translation_field, orig_type, nullable=(not self._is_required(lang, field, options))
                )

                model.__table__.append_column(column)

                # change model Pydatnic field
                pydantic_field = deepcopy(model.model_fields[field])

                pydantic_field.alias = translation_field
                pydantic_field.annotation = translation_annotation

                model.model_fields[translation_field] = pydantic_field
                model.__annotations__[translation_field] = translation_annotation

                setattr(model, translation_field, column_property(column))

        model.model_rebuild(force=True)

    def _make_optional(self, typehint: Any) -> Any:
        """Wrap a type in Optional[] unless it's already optional."""
        origin = get_origin(typehint)
        if origin is Union and type(None) in get_args(typehint):
            return typehint
        return typehint | None

    def _is_required(self, language: str, field: str, options: TranslationOptions) -> bool:
        if options.required_languages is None:
            return False
        if type(options.required_languages) is tuple:
            return language in options.required_languages
        if language in options.required_languages:
            return field in options.required_languages[language]
        if "default" in options.required_languages:
            return field in options.required_languages["default"]
        return False

    def _is_null_value(self, field: str, value: Any, options: TranslationOptions) -> bool:
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

    def _yield_fallbacks(self, language: str, fallbacks: dict[str, tuple[str, ...]] | None) -> Iterator[str]:
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

    def _fallback_value(self, field: str, options: TranslationOptions) -> Any:
        if options.fallback_values is None:
            return None
        if type(options.fallback_languages) is not dict:
            return options.fallback_values
        if field in options.fallback_values:
            return options.fallback_values[field]
        return None
