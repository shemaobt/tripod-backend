from typing import Any, Required, TypedDict

from app.services.book_context.generation.types import BHSAEntity, CommonNounCandidate


class BCDGenerationState(TypedDict, total=False):
    """LangGraph state for BCD generation.

    Fields marked `Required[]` are part of the initial input and are guaranteed
    to be present when the graph is invoked. The remaining fields are populated
    by intermediate nodes and are absent until then.
    """

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
