from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, cast

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from advanced_alchemy.exceptions import ConflictError, RepositoryError

if TYPE_CHECKING:
    from sqlalchemy.orm import InstrumentedAttribute

    from advanced_alchemy.base import ModelProtocol
    from advanced_alchemy.repository.typing import ModelT


@contextmanager
def wrap_sqlalchemy_exception() -> Any:
    """Do something within context to raise a `RepositoryError` chained
    from an original `SQLAlchemyError`.

        >>> try:
        ...     with wrap_sqlalchemy_exception():
        ...         raise SQLAlchemyError("Original Exception")
        ... except RepositoryError as exc:
        ...     print(f"caught repository exception from {type(exc.__context__)}")
        ...
        caught repository exception from <class 'sqlalchemy.exc.SQLAlchemyError'>
    """
    try:
        yield
    except IntegrityError as exc:
        raise ConflictError from exc
    except SQLAlchemyError as exc:
        msg = f"An exception occurred: {exc}"
        raise RepositoryError(msg) from exc
    except AttributeError as exc:
        raise RepositoryError from exc


def get_instrumented_attr(model: type[ModelProtocol], key: str | InstrumentedAttribute) -> InstrumentedAttribute:
    if isinstance(key, str):
        return cast("InstrumentedAttribute", getattr(model, key))
    return key


def model_from_dict(model: ModelT, **kwargs: Any) -> ModelT:
    """Return ORM Object from Dictionary."""
    data = {}
    for column in model.__table__.columns:
        column_val = kwargs.get(column.name, None)
        if column_val is not None:
            data[column.name] = column_val
    return model(**data)  # type: ignore  # noqa: PGH003
