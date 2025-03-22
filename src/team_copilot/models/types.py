"""Team Copilot - Core - Types."""

from sqlalchemy.types import UserDefinedType


class VectorType(UserDefinedType):
    """PostgreSQL vector type."""

    def __init__(self, precision=1024):
        """Initialize the vector type.

        Args:
            precision (int): Precision.
        """
        self.precision = precision

    def get_col_spec(self, **kwargs):
        """Get the column specification.

        The column specification is the SQL string that defines the column in
        the database. The specification is used during the table creation
        through SQLAlchemy.
        """
        return f"vector({self.precision})"

    def bind_processor(self, dialect):
        """Return a function that converts Python values to database values.

        E.g. [1, 2, 3] would be converted to "[1, 2, 3]".
        """
        return lambda value: value if value is None else str(value)

    def result_processor(self, dialect, coltype):
        """Return a function that converts database values to Python values.

        E.g. "[1, 2, 3]" would be converted to [1, 2, 3].
        """
        return lambda value: value
