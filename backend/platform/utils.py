from fastapi import Request


def trace_id_from_request(request: Request) -> str:
    return getattr(request.state, "trace_id", "n/a")


def paginate_sql(base_query: str, page: int, page_size: int, sort_by: str = "id", sort_dir: str = "desc") -> str:
    sort_dir = "ASC" if sort_dir.lower() == "asc" else "DESC"
    offset = max(0, (page - 1) * page_size)
    return f"{base_query} ORDER BY {sort_by} {sort_dir} LIMIT {page_size} OFFSET {offset}"
