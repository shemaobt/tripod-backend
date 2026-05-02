from typing import Any, Required, TypedDict

from app.services.book_context.generation.types import BHSAEntity, CommonNounCandidate


class BCDGenerationState(TypedDict, total=False):
    book_name: Required[str]
    book_id: Required[str]
    bcd_id: Required[str]
    genre: Required[str]
    chapter_count: Required[int]
    bhsa_summary: str
    bhsa_entities: list[BHSAEntity]
    bhsa_common_nouns: list[CommonNounCandidate]
    structural_outline: dict[str, Any]
    participant_register: list[dict[str, Any]]
    discourse_threads: list[dict[str, Any]]
    theological_spine: str
    places: list[dict[str, Any]]
    objects: list[dict[str, Any]]
    institutions: list[dict[str, Any]]
    genre_context: dict[str, Any]
    maintenance_notes: dict[str, Any]
    user_feedback: str
