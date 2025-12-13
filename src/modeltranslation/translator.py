from contextvars import ContextVar
from copy import deepcopy

from sqlalchemy import Column
from sqlalchemy.orm import column_property
from sqlmodel import SQLModel
from sqlmodel.main import SQLModelMetaclass


class TranslationOptions:
    fields: tuple[str] = ()
    languages: tuple[str] = ()


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

    def register(self, model: type[SQLModel]):
        def decorator(options: type[TranslationOptions]) -> None:
            self._replace_accessors(model, options)
            self._rebuild_model(model, options)

        return decorator

    def _replace_accessors(
        self, model: type[SQLModel], translation_options: TranslationOptions
    ) -> type[SQLModel]:
        original_getattribute = model.__getattribute__
        original_setattr = model.__setattr__

        def new_getattribute(model_self: SQLModel, name: str) -> any:
            if name.startswith("_") or name not in translation_options.fields:
                return original_getattribute(model_self, name)

            current_locale = self.get_locale()
            default_locale = self.get_default_locale()

            # TODO: implement returning the default value in case if translation field value is empty  # noqa: E501, FIX002
            if current_locale in translation_options.languages:
                return original_getattribute(model_self, f"{name}_{current_locale}")

            return original_getattribute(model_self, f"{name}_{default_locale}")

        def new_setattr(model_self: SQLModel, name: str, value: any) -> None:
            if name.startswith("_") or name not in translation_options.fields:
                return original_setattr(model_self, name, value)

            current_locale = self.get_locale()
            default_locale = self.get_default_locale()

            if current_locale in translation_options.languages:
                return original_setattr(model_self, f"{name}_{current_locale}", value)

            return original_setattr(model_self, name, f"{name}_{default_locale}")

        class LocalizedMeta(SQLModelMetaclass):
            def __getattribute__(model_self, name: str) -> any:
                current_locale = self.get_locale()

                if name in translation_options.fields:
                    localized = f"{name}_{current_locale}"
                    if hasattr(model, localized):
                        return getattr(model, localized)
                return super().__getattribute__(name)

        model.__class__ = LocalizedMeta
        model.__getattribute__ = new_getattribute
        model.__setattr__ = new_setattr
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
