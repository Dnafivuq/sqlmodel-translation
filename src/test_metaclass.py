from sqlmodel import Field, SQLModel
from sqlmodel.main import SQLModelMetaclass


class TranslationOptions:
    fields: tuple[str] = ()
    languages: tuple[str] = ()


class BookTranslationOptions(TranslationOptions):
    fields = ("title",)
    languages = ("pl",)


class TranslatorMetaclass(SQLModelMetaclass):
    def __new__(cls, name: str, bases: tuple, namespace: dict, **kwargs):
        annotations = namespace.setdefault("__annotations__", {})

        fields = kwargs["translation_options"].fields
        languages = kwargs["translation_options"].languages

        for field in fields:
            if field in annotations and (
                annotations[field] == (str | None) or annotations[field] is str
            ):
                for language in languages:
                    annotations[f"{field}_{language}"] = str | None
                    namespace[f"{field}_{language}"] = Field(default=None)

        return super().__new__(cls, name, bases, namespace, **kwargs)


class Book(
    SQLModel,
    table=True,
    metaclass=TranslatorMetaclass,
    translation_options=BookTranslationOptions,
):
    id: int = Field(primary_key=True)
    title: str | None


print(Book.model_fields)
print(Book.__table__.columns)
