# SQLModel-translation
SQLModel-translation is a library for translating SQLModel with FastAPI apps.
This library was heavily inspired by [django-modeltranslation](https://django-modeltranslation.readthedocs.io/en/latest/)

## Features
- Apply translations without modifying existing SQLModel classes.
- Write SQLModel queries without having to worry about the language.
- Automatically translate requests based on `Accept-Language` HTTP header.
- Fully compatible with Pydantic validation.


See [quickstart](quickstart.md), [reference](reference.md) and [concepts](concepts.md) for more details.