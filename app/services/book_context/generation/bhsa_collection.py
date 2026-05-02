from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from app.services.book_context.generation.bhsa_stream import stream_book_clauses
from app.services.book_context.generation.types import (
    BHSAEntity,
    BHSAEntryRef,
    ClauseExtract,
    CollectBHSAOutput,
    CommonNounCandidate,
)

_PERSON_TYPES = frozenset({"pers", "ppde", "pers,gens", "pers,god"})
_PLACE_TYPES = frozenset({"topo", "gens,topo"})
_SKIP_TYPES = frozenset({"mens"})

_TOP_N = 250
_MIN_APPEARANCES = 2
_NOMINAL_FUNCTIONS = frozenset({"Subj", "Objc", "Cmpl", "PreC"})
_SAMPLE_LIMIT = 8


def _min_appearances_for(chapter_count: int) -> int:
    return 1 if chapter_count <= 4 else _MIN_APPEARANCES


def _classify_nametype(nametype: str) -> str:
    if nametype in _PERSON_TYPES:
        return "person"
    if nametype in _PLACE_TYPES:
        return "place"
    if nametype in _SKIP_TYPES:
        return "skip"
    if "pers" in nametype:
        return "person"
    if "topo" in nametype:
        return "place"
    return "ambiguous"


@dataclass
class _SummaryAcc:
    lines: list[str] = field(default_factory=list)
    current_ch: int | None = None
    clause_count: int = 0
    all_names: set[str] = field(default_factory=set)
    verbs: list[str] = field(default_factory=list)
    verse_summaries: dict[int, list[str]] = field(default_factory=dict)


def _summary_flush_chapter(acc: _SummaryAcc) -> None:
    if acc.current_ch is None:
        return
    acc.lines.append(f"\n=== Chapter {acc.current_ch} ({acc.clause_count} clauses) ===")
    if acc.all_names:
        acc.lines.append(f"  Names: {', '.join(sorted(acc.all_names))}")
    if acc.verbs:
        acc.lines.append(f"  Key verbs: {', '.join(acc.verbs[:20])}")
    for v in sorted(acc.verse_summaries.keys()):
        combined = " | ".join(acc.verse_summaries[v][:3])
        acc.lines.append(f"  v{v}: {combined[:200]}")


def summary_start_chapter(acc: _SummaryAcc, ch: int) -> None:
    _summary_flush_chapter(acc)
    acc.current_ch = ch
    acc.clause_count = 0
    acc.all_names = set()
    acc.verbs = []
    acc.verse_summaries = {}


def summary_consume(acc: _SummaryAcc, ch: int, clause: ClauseExtract) -> None:
    acc.clause_count += 1
    v = clause["verse"]
    if v not in acc.verse_summaries:
        acc.verse_summaries[v] = []
    gloss = clause.get("gloss", "")
    if gloss:
        acc.verse_summaries[v].append(gloss[:120])
    for name in clause.get("names", []):
        acc.all_names.add(name)
    if clause.get("lemma"):
        acc.verbs.append(
            f"{clause['lemma']} ({clause.get('binyan', '?')}/{clause.get('tense', '?')})"
        )


def summary_build(acc: _SummaryAcc) -> str:
    _summary_flush_chapter(acc)
    return "\n".join(acc.lines)


@dataclass
class _EntitiesAcc:
    appearances: dict[str, list[BHSAEntryRef]] = field(default_factory=dict)
    first: dict[str, BHSAEntryRef] = field(default_factory=dict)
    last: dict[str, BHSAEntryRef] = field(default_factory=dict)
    glosses: dict[str, str] = field(default_factory=dict)
    types: dict[str, str] = field(default_factory=dict)


def entities_consume(acc: _EntitiesAcc, ch: int, clause: ClauseExtract) -> None:
    v = clause["verse"]
    ref: BHSAEntryRef = {"chapter": ch, "verse": v}

    for name in clause.get("names", []):
        if name not in acc.appearances:
            acc.appearances[name] = []
            acc.first[name] = ref
        if not acc.appearances[name] or acc.appearances[name][-1] != ref:
            acc.appearances[name].append(ref)
        acc.last[name] = ref

    for heb_name, gloss in clause.get("name_glosses", {}).items():
        if heb_name not in acc.glosses and gloss:
            acc.glosses[heb_name] = gloss

    for heb_name, nt in clause.get("name_types", {}).items():
        if heb_name not in acc.types and nt:
            acc.types[heb_name] = nt


def entities_build(acc: _EntitiesAcc) -> list[BHSAEntity]:
    entities: list[BHSAEntity] = []
    for name in sorted(acc.appearances.keys()):
        raw_nametype = acc.types.get(name, "")
        entity_type = _classify_nametype(raw_nametype) if raw_nametype else "ambiguous"
        if entity_type == "skip":
            continue
        entities.append(
            {
                "name": name,
                "english_gloss": acc.glosses.get(name, ""),
                "entity_type": entity_type,
                "entry_verse": acc.first[name],
                "exit_verse": acc.last[name],
                "appears_in": acc.appearances[name],
                "appearance_count": len(acc.appearances[name]),
            }
        )
    return entities


@dataclass
class _CommonNounsAcc:
    min_appearances: int = _MIN_APPEARANCES
    aggregates: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)


def common_nouns_consume(acc: _CommonNounsAcc, ch: int, clause: ClauseExtract) -> None:
    v = clause["verse"]
    ref: BHSAEntryRef = {"chapter": ch, "verse": v}
    for cw in clause.get("content_words", []):
        key_lex = cw.get("lex_utf8") or cw.get("lex")
        sp = cw.get("sp")
        if not key_lex or not sp:
            continue
        key = (key_lex, sp)

        bucket = acc.aggregates.get(key)
        if bucket is None:
            bucket = {
                "lex_utf8": cw.get("lex_utf8"),
                "lex": cw.get("lex"),
                "sp": sp,
                "english_gloss": cw.get("gloss") or "",
                "first_appears": ref,
                "appears_in": [],
                "function_counter": Counter(),
                "binyan_counter": Counter(),
            }
            acc.aggregates[key] = bucket

        if not bucket["english_gloss"] and cw.get("gloss"):
            bucket["english_gloss"] = cw["gloss"]

        if not bucket["appears_in"] or bucket["appears_in"][-1] != ref:
            bucket["appears_in"].append(ref)

        func = cw.get("function")
        if func:
            bucket["function_counter"][func] += 1
        binyan = cw.get("binyan")
        if binyan:
            bucket["binyan_counter"][binyan] += 1


def common_nouns_build(acc: _CommonNounsAcc) -> list[CommonNounCandidate]:
    candidates: list[CommonNounCandidate] = []
    for bucket in acc.aggregates.values():
        appearance_count = len(bucket["appears_in"])
        if appearance_count < acc.min_appearances:
            continue

        sp = bucket["sp"]
        function_counter: Counter = bucket["function_counter"]

        if sp in ("subs", "adjv") and not (set(function_counter.keys()) & _NOMINAL_FUNCTIONS):
            continue

        candidates.append(
            {
                "lemma": bucket["lex_utf8"],
                "lemma_ascii": bucket["lex"],
                "english_gloss": bucket["english_gloss"],
                "sp": sp,
                "appearance_count": appearance_count,
                "top_functions": [f for f, _ in function_counter.most_common(3)],
                "top_binyans": [b for b, _ in bucket["binyan_counter"].most_common(3)],
                "first_appears": bucket["first_appears"],
                "sample_appears_in": bucket["appears_in"][:_SAMPLE_LIMIT],
            }
        )

    candidates.sort(key=lambda c: c["appearance_count"], reverse=True)
    return candidates[:_TOP_N]


def collect_bhsa_data(tf_api: Any, book_name: str, chapter_count: int) -> CollectBHSAOutput:
    summary = _SummaryAcc()
    entities = _EntitiesAcc()
    common = _CommonNounsAcc(min_appearances=_min_appearances_for(chapter_count))

    for chapter_data in stream_book_clauses(tf_api, book_name, chapter_count):
        ch = chapter_data["chapter"]
        summary_start_chapter(summary, ch)
        for clause in chapter_data["clauses"]:
            summary_consume(summary, ch, clause)
            entities_consume(entities, ch, clause)
            common_nouns_consume(common, ch, clause)

    return CollectBHSAOutput(
        bhsa_summary=summary_build(summary),
        bhsa_entities=entities_build(entities),
        bhsa_common_nouns=common_nouns_build(common),
    )
