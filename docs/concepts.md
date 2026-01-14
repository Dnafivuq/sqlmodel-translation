# Concepts

This section will explain several concepts in closer detail for when the reference might not be sufficient.

## Registering models
SQLModel-translation can translate fields of SQLModel classes without modifying the original class.

Consider the following example which translates `Book` into english and polish.

```python
from modeltranslation import Translator, TranslationOptions
from sqlmodel import SQLModel


class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str

translator = Translator(
    default_language="en",
    languages=("en", "pl"),
)

@translator.register(Book)
class BookTranslationOptions(TranslationOptions):
    fields = ("title",)
    required_languages = ("en",)

```
In practice `Book` now looks like this.

```python
class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str | None
    title_pl: str | None
    title_en: str
```
The pydantic model stays correct and as strict as possible.



Let's see a more complicated example and explain it step by step.

```python
from modeltranslation import Translator, TranslationOptions
from sqlmodel import SQLModel

class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: str

translator = Translator(
    default_language="en",
    languages=("en", "pl", "fr", "es"),
    fallback_languages={"fr": ("pl", "en"), "default": ("fr",)},
)

@translator.register(Book)
class BookTranslationOptions(TranslationOptions):
    fields = ("title",)
    required_languages = {"fr": ("title", "author"), "default": ("title",)}
    fallback_values = {"title": ("Title"), "author": ("No translation provided")}
```

1. `fallback_languages={"fr": ("es", "pl"), "default": ("en",)}`
    This means that when there is no value for french, spanish and polish will be tried next.
    For other languages `en` will be used as the first fallback.


2. `required_languages = {"fr": ("title", "author"), "default": ("title",)}`
Title is required in all languages. Additionally the author is required to be translated in french.


3. `fallback_values = {"title": ("Title"), "author": ("No translation provided")`
When language fallbacks fail then fallback values will be used instead.


### Exceptions
Sometimes the translation configuration can be inconsistent. For example:

```python
from modeltranslation import Translator, TranslationOptions

translator = Translator(
    default_language="en",
    languages=("en", "pl"),
)

class BookTranslationOptions(TranslationOptions):
    fields = ("title",)
    required_languages = ("fr")
```
This is impossible, because `fr` is not declared in the translator.
[ImproperlyConfiguredError][modeltranslation.ImproperlyConfiguredError] will be thrown whenever inconsistencies like this are detected.

For more details about possible configuraion options see [`Translator`][modeltranslation.Translator] and [`TranslationOptions`][modeltranslation.TranslationOptions]. If this is not sufficient try looking up the tests.
Each test for a configuration option is an example exactly like this and is fairly readable to new users.


## Accessing translated fields

__Rule 1__
    Reading the value from the original field returns the value translated to the current language.

__Rule 2__
    Assigning a value to the original field updates the value in the associated current language translation field.

__Rule 3__
    If both fields - the original and the current language translation field - are updated at the same time, the current language translation field wins.

The original field is inaccessible and should be considered invalid.

## Using SQLModel queries

Registering translations makes all SQLModel queries work with the new translation fields.

For example:
```python
update(Book).where(Book.author == "J.R.R. Tolkien").values(title="translation")
select(Book).where(Book.title_en == "english_title")
```

There is one exception which might feel unnatural.

```python
select(Book.title)
select(Book.title_en)
```

Selecting columns only reroutes to the correct column based on the active langugage.
This means that any fallback languages or values configured both in [`Translator`][modeltranslation.Translator], [`TranslationOptions`][modeltranslation.TranslationOptions] and will not apply here.