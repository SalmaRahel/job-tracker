"""Validates Gemini-written SQL before it is run; returns safe SQL or raises UnsafeSQLError."""
import sqlglot
from sqlglot import exp
from sqlglot.dialects.dialect import Dialect
from sqlglot.errors import SqlglotError

from src.config import settings

DIALECT = "postgres"
MAX_SQL_LENGTH = 2000

ALLOWED_TABLE = "job"
ALLOWED_COLUMNS = frozenset({
    "id", "created_at", "company_name", "position", "location",
    "application_date", "deadline", "status",
})
HIDDEN_COLUMNS = frozenset({"user_id", "job_description", "job_link", "search_vector"})

ALLOWED_FUNCTIONS = (
    exp.Count, exp.Sum, exp.Min, exp.Max, exp.Avg,
    exp.Lower, exp.Upper, exp.Length, exp.Round, exp.Coalesce,
    exp.Cast, exp.Extract, exp.CurrentDate, exp.CurrentTimestamp,
    exp.TimestampTrunc, exp.DateTrunc,
    exp.And, exp.Or, exp.Case, exp.If,
)

ALLOWED_CAST_TYPES = frozenset({
    exp.DataType.Type.INT, exp.DataType.Type.BIGINT, exp.DataType.Type.SMALLINT,
    exp.DataType.Type.TEXT, exp.DataType.Type.VARCHAR, exp.DataType.Type.CHAR,
    exp.DataType.Type.DATE, exp.DataType.Type.TIMESTAMP, exp.DataType.Type.TIMESTAMPTZ,
    exp.DataType.Type.BOOLEAN, exp.DataType.Type.DECIMAL,
    exp.DataType.Type.DOUBLE, exp.DataType.Type.FLOAT,
})

FORBIDDEN_NODES = (
    exp.With, exp.Union, exp.Intersect, exp.Except,
    exp.Into, exp.Lock,
    exp.Parameter, exp.Placeholder,
    exp.Command, exp.Fetch,
)


class UnsafeSQLError(Exception):
    """SQL is not allowed; `reason` is for logs only."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def validate_sql(sql: str, max_rows: int | None = None) -> str:
    if max_rows is None:
        max_rows = settings.job_search_max_rows

    if not isinstance(sql, str) or not sql.strip():
        raise UnsafeSQLError("empty query")
    if len(sql) > MAX_SQL_LENGTH:
        raise UnsafeSQLError("query too long")

    _reject_comments(sql)
    tree = _parse_single_select(sql)
    _reject_forbidden_nodes(tree)
    _reject_quoted_identifiers(tree)
    table_names = _check_tables(tree)
    _check_functions(tree)
    _check_casts_and_intervals(tree)
    _check_stars(tree)
    _check_columns(tree, table_names)
    tree = _enforce_limit(tree, max_rows)
    return tree.sql(dialect=DIALECT)


def _reject_comments(sql: str) -> None:
    try:
        tokens = Dialect.get_or_raise(DIALECT).tokenize(sql)
    except SqlglotError:
        raise UnsafeSQLError("could not tokenize")
    if any(token.comments for token in tokens):
        raise UnsafeSQLError("comments are not allowed")


def _parse_single_select(sql: str) -> exp.Select:
    try:
        statements = sqlglot.parse(sql, dialect=DIALECT)
    except SqlglotError:
        raise UnsafeSQLError("could not parse")
    if len(statements) != 1 or statements[0] is None:
        raise UnsafeSQLError("exactly one statement is allowed")
    tree = statements[0]
    if type(tree) is not exp.Select:
        raise UnsafeSQLError(f"only SELECT is allowed, got {type(tree).__name__}")
    return tree


def _reject_forbidden_nodes(tree: exp.Select) -> None:
    for node in tree.walk():
        if isinstance(node, FORBIDDEN_NODES):
            raise UnsafeSQLError(f"forbidden construct: {type(node).__name__}")


def _reject_quoted_identifiers(tree: exp.Select) -> None:
    for ident in tree.find_all(exp.Identifier):
        if ident.args.get("quoted"):
            raise UnsafeSQLError("quoted identifiers are not allowed")


def _check_tables(tree: exp.Select) -> set[str]:
    qualifiers = {ALLOWED_TABLE}
    for table in tree.find_all(exp.Table):
        if not isinstance(table.this, exp.Identifier):
            raise UnsafeSQLError("table-valued function in FROM")
        if table.db or table.catalog:
            raise UnsafeSQLError("schema-qualified table")
        if table.name.lower() != ALLOWED_TABLE:
            raise UnsafeSQLError(f"table not allowed: {table.name}")
        if table.alias:
            qualifiers.add(table.alias.lower())
    return qualifiers


def _check_functions(tree: exp.Select) -> None:
    for node in tree.walk():
        if isinstance(node, exp.Func) and not isinstance(node, ALLOWED_FUNCTIONS):
            name = node.name if isinstance(node, exp.Anonymous) else type(node).__name__
            raise UnsafeSQLError(f"function not allowed: {name}")


def _check_casts_and_intervals(tree: exp.Select) -> None:
    for cast in tree.find_all(exp.Cast):
        to = cast.args.get("to")
        if not isinstance(to, exp.DataType) or to.this not in ALLOWED_CAST_TYPES:
            raise UnsafeSQLError("cast to this type is not allowed")
    for interval in tree.find_all(exp.Interval):
        value = interval.this
        if not isinstance(value, exp.Literal) or len(value.name) > 30:
            raise UnsafeSQLError("interval must be a short literal, e.g. interval '14 days'")


def _check_stars(tree: exp.Select) -> None:
    for star in tree.find_all(exp.Star):
        if not isinstance(star.parent, exp.Count):
            raise UnsafeSQLError("SELECT * is not allowed")


def _check_columns(tree: exp.Select, table_names: set[str]) -> None:
    for select in tree.find_all(exp.Select):
        for projection in select.expressions:
            if isinstance(projection, exp.Alias) and projection.alias.lower() in HIDDEN_COLUMNS:
                raise UnsafeSQLError("alias shadows a hidden column")

    for column in tree.find_all(exp.Column):
        if isinstance(column.this, exp.Star):
            continue
        name = column.name.lower()
        qualifier = column.table.lower()
        if qualifier and qualifier not in table_names:
            raise UnsafeSQLError(f"unknown table qualifier: {qualifier}")
        if name in ALLOWED_COLUMNS:
            continue
        if not qualifier and _is_bare_order_or_group_alias(column, name):
            continue
        raise UnsafeSQLError(f"column not allowed: {name}")


def _is_bare_order_or_group_alias(column: exp.Column, name: str) -> bool:
    parent = column.parent
    in_order = isinstance(parent, exp.Ordered) and isinstance(parent.parent, exp.Order)
    in_group = isinstance(parent, exp.Group)
    if not (in_order or in_group):
        return False
    select = column.find_ancestor(exp.Select)
    if select is None:
        return False
    aliases = {p.alias.lower() for p in select.expressions if isinstance(p, exp.Alias)}
    return name in aliases


def _enforce_limit(tree: exp.Select, max_rows: int) -> exp.Select:
    limit = tree.args.get("limit")
    if isinstance(limit, exp.Limit):
        value = limit.expression
        if isinstance(value, exp.Literal) and not value.is_string:
            try:
                if int(value.name) <= max_rows:
                    return tree
            except ValueError:
                pass
    return tree.limit(max_rows, copy=False)
