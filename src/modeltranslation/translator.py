from contextvars import ContextVar
from copy import deepcopy
from functools import wraps
from typing import Callable

from sqlalchemy import Column
from sqlalchemy.orm import column_property
from sqlmodel import SQLModel
from sqlmodel.main import SQLModelMetaclass


class TranslationOptions:
    fields: tuple[str] = ()
    fallback_languages: dict[str, tuple[str]] = None
    fallback_values: dict[str, any] | any = None
    fallback_undefined: dict[str, any] = None
    required_languages: dict[str, tuple[str]] | tuple[str] = None


class Translator:
    def __init__(self, default_locale: str) -> None:
        self._current_locale: ContextVar[str] = ContextVar("current_locale", default="en")
        self._default_locale: str = default_locale

    def get_locale(self) -> str:
        return self._current_locale.get()

    def set_locale(self, locale: str) -> None:
        self._current_locale.set(locale)

    def get_default_locale(self) -> str:
        return self._default_locale

    def register(self, model: type[SQLModel]) -> Callable:
        def decorator(options: type[TranslationOptions]) -> None:
            self._replace_accessors(model, options)
            self._rebuild_model(model, options)

        return decorator

    def _replace_accessors(
        self, model: type[SQLModel], translation_options: TranslationOptions
    ) -> type[SQLModel]:

        def locale_decorator(original_function: Callable) -> Callable:
            @wraps(original_function)
            def locale_function(model_self: SQLModel, name: str, *args: any) -> any:
                # ignore private functions
                if name.startswith("_") or name not in translation_options.fields:
                    return original_function(model_self, name, *args)

                current_locale = self.get_locale()
                default_locale = self.get_default_locale()

                if current_locale in translation_options.languages:
                    return original_function(model_self, f"{name}_{current_locale}", *args)

                return original_function(model_self, f"{name}_{default_locale}", *args)

            return locale_function

        model.__class__.__getattribute__ = locale_decorator(model.__class__.__getattribute__)
        model.__getattribute__ = locale_decorator(model.__getattribute__)
        model.__setattr__ = locale_decorator(model.__setattr__)
        return model

    def _rebuild_model(self, model: type[SQLModel], translation_options: TranslationOptions) -> None:
        for field in translation_options.fields:
            for lang in translation_options.languages:
                field_name = f"{field}_{lang}"

                # TODO: check if field type is translatable
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
