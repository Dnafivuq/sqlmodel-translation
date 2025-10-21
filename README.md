# Design Proposal

The goal of this project is to write a model translation library compatible with FastAPI and SQLModel.

## Planned functionality

We are basing the functionality on the [django-modeltranslation](https://django-modeltranslation.readthedocs.io/en/latest/) library. This includes:

- Lazy translation of Pydantic models  
- Simple management of language/locale  
- Automatic language selection for SQLModels based on detected language  
- Straightforward declaration of translated variations of SQLModel fields  
- Easy integration with FastAPI without modifying existing endpoints

## Planned experiments

1. Creating a simple mock application to test usability and user friendliness on the prototype for assessing correctness of our idea and approach.  
2. Creating a simple use case with FastApi/SQLModel and Django model translation, to directly compare features, usability and performance against our implementation  
3. Testing a complete external FastAPI and SQLModel application to identify potential issues when integrating the library into an existing project.

## Tech stack

| Category | Technology |
| :---- | :---- |
| Frameworks | FastAPI, SQLModel, Pydantic, SQLite, Babel |
| Formatter and linter | ruff |
| Documentation | MkDocs with mkdocstrings |
| Testing | pytest, HTTPX, tox |
| Package building and management | uv |
| CI/CD | github workflows/actions |

## Schedule

| Week | Start date | Planned work |
| :---- | :---- | :---- |
| 1 | 20/10/25 | Configuring dependencies and tools. Setting up simple use cases and experimenting with possible solutions. |
| 2 | 27/10/25 | Creating a prototype. |
| 3 | 3/11/25 | Finishing and polishing the prototype. |
| 4..5 | 10/11/25 | None (2 weeks full of university tests) |
| 6 | 24/11/25 | Experimenting and planning future work. |
| 7..9 | 01/12/25 | Implementing features for real world use cases. |
| 10 | 22/12/25 | Testing on existing projects and fixing compatibility issues. |
| 11 | 29/12/25 | Finalizing public API and finishing documentation. |
| 12 | 05/01/26 | Publishing the package |
| 13..14 | 12/01/26 | Schedule reserve / hotfixing issues. |

### Major deadlines

- 7.11.25 \- working prototype deadline.  
- 15.01.26 \- project submission deadline for exemption from the second test.  
- 23.01.26 \- final submission deadline.

## References

[https://django-modeltranslation.readthedocs.io/en/latest/](https://django-modeltranslation.readthedocs.io/en/latest/)  
[https://sqlmodel.tiangolo.com/](https://sqlmodel.tiangolo.com/)  
[https://docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/)  
[https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)  
[https://babel.pocoo.org/en/latest/index.html](https://babel.pocoo.org/en/latest/index.html)
