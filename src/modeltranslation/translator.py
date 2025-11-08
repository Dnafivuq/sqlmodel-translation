from contextvars import ContextVar

from sqlmodel import Field, SQLModel
from sqlmodel.main import SQLModelMetaclass


class Translator:
    _current_locale: ContextVar[str] = ContextVar("current_locale", default="en")
    _default_locale: str = "pl"

    @classmethod
    def get_locale(cls) -> str:
        return cls._current_locale.get()

    @classmethod
    def set_locale(cls, locale: str) -> None:
        cls._current_locale.set(locale)

    @classmethod
    def get_default_locale(cls) -> str:
        return cls._default_locale


class TranslationOptions:
    fields: tuple[str] = ()
    languages: tuple[str] = ()


"""
@register(News)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'text',)

class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'text',)
    required_languages = {'de': ('title', 'text'), 'default': ('title',)}

https://django-modeltranslation.readthedocs.io/en/latest/installation.html#languages
"""


def register(cls: type[SQLModel], translation_options: TranslationOptions) -> type[SQLModel]:
    original_getattribute = cls.__getattribute__
    original_setattr = cls.__setattr__

    def new_getattribute(self: SQLModel, name: str) -> any:
        if name.startswith("_") or name not in translation_options.fields:
            return original_getattribute(self, name)

        current_locale = Translator.get_locale()
        default_locale = Translator.get_default_locale()

        # TODO: implement returning the default value in case if translation field value is empty  # noqa: E501, FIX002
        if current_locale in translation_options.languages:
            return original_getattribute(self, f"{name}_{current_locale}")

        return original_getattribute(self, f"{name}_{default_locale}")

    def new_setattr(self: SQLModel, name: str, value: any) -> None:
        if name.startswith("_") or name not in translation_options.fields:
            return original_setattr(self, name, value)

        current_locale = Translator.get_locale()
        default_locale = Translator.get_default_locale()

        if current_locale in translation_options.languages:
            return original_setattr(self, f"{name}_{current_locale}", value)

        return original_setattr(self, name, f"{name}_{default_locale}")

    class LocalizedMeta(SQLModelMetaclass):
        def __getattribute__(self, name: str) -> any:
            current_locale = Translator.get_locale()

            if name in translation_options.fields:
                localized = f"{name}_{current_locale}"
                if hasattr(cls, localized):
                    return getattr(cls, localized)
            return super().__getattribute__(name)

    cls.__class__ = LocalizedMeta
    cls.__getattribute__ = new_getattribute
    cls.__setattr__ = new_setattr
    return cls


class TranslatorMetaclass(SQLModelMetaclass):
    def __new__(cls, name: str, bases: tuple, namespace: dict, **kwargs: dict[str]) -> "TranslatorMetaclass":
        annotations = namespace.setdefault("__annotations__", {})

        fields = kwargs["translation_options"].fields
        languages = kwargs["translation_options"].languages

        for field in fields:
            if field in annotations and (annotations[field] == (str | None) or annotations[field] is str):
                for language in languages:
                    annotations[f"{field}_{language}"] = str | None
                    namespace[f"{field}_{language}"] = Field(default=None)

        return super().__new__(cls, name, bases, namespace, **kwargs)
