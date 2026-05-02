from __future__ import annotations

from typing import Any

from app.services.book_context.generation.bhsa_collection import (
    _SummaryAcc,
    summary_build,
    summary_consume,
    summary_start_chapter,
)
from app.services.book_context.generation.bhsa_stream import stream_book_clauses


def build_bhsa_summary(tf_api: Any, book_name: str, chapter_count: int) -> str:
    acc = _SummaryAcc()
    for chapter_data in stream_book_clauses(tf_api, book_name, chapter_count):
        ch = chapter_data["chapter"]
        summary_start_chapter(acc, ch)
        for clause in chapter_data["clauses"]:
            summary_consume(acc, ch, clause)
    return summary_build(acc)
