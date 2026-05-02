from app.services.book_context.generation.state import BCDGenerationState


def test_state_can_be_created_with_required_fields():
    state: BCDGenerationState = {
        "book_name": "Ruth",
        "book_id": "abc-123",
        "bcd_id": "bcd-456",
        "genre": "narrative",
        "chapter_count": 4,
    }
    assert state["book_name"] == "Ruth"
    assert state["chapter_count"] == 4


def test_state_accepts_all_fields():
    state: BCDGenerationState = {
        "book_name": "Ruth",
        "book_id": "abc-123",
        "bcd_id": "bcd-456",
        "genre": "narrative",
        "chapter_count": 4,
        "bhsa_summary": "summary text",
        "bhsa_entities": [{"name": "Ruth", "entry_verse": {"chapter": 1, "verse": 4}}],
        "bhsa_common_nouns": [
            {"lemma": "שדה", "sp": "subs", "english_gloss": "field", "appearance_count": 5}
        ],
        "structural_outline": {"book_arc": "test"},
        "participant_register": [{"name": "Naomi"}],
        "discourse_threads": [],
        "theological_spine": "spine text",
        "places": [],
        "objects": [],
        "institutions": [],
        "genre_context": {},
        "maintenance_notes": {},
    }
    assert state["bhsa_summary"] == "summary text"
    assert state["structural_outline"]["book_arc"] == "test"
    assert len(state["bhsa_entities"]) == 1
    assert state["bhsa_common_nouns"][0]["lemma"] == "שדה"


def test_shared_context_includes_common_nouns():
    from app.services.book_context.generation.nodes.context_sections import (
        _build_shared_context,
    )

    state: BCDGenerationState = {
        "book_name": "Ruth",
        "book_id": "abc",
        "bcd_id": "bcd",
        "genre": "narrative",
        "chapter_count": 4,
        "bhsa_common_nouns": [
            {"lemma": "שדה", "sp": "subs", "english_gloss": "field", "appearance_count": 6},
        ],
    }
    ctx = _build_shared_context(state)
    assert "common_nouns" in ctx
    assert "שדה" in ctx["common_nouns"]
    assert "field" in ctx["common_nouns"]


def test_bhsa_stream_generator_structure():
    from app.services.book_context.generation.bhsa_stream import stream_book_clauses

    assert callable(stream_book_clauses)


def test_schemas_validate():
    from app.services.book_context.generation.schemas import (
        ContextSectionsSchema,
        DiscourseThreadsSchema,
        GenreContextSchema,
        MaintenanceNotesSchema,
        ParticipantRegisterSchema,
        StructuralOutlineSchema,
    )

    outline = StructuralOutlineSchema(
        book_arc="The arc of Ruth",
        chapters=[],
        literary_structure="linear",
    )
    assert outline.book_arc == "The arc of Ruth"

    participants = ParticipantRegisterSchema(participants=[])
    assert len(participants.participants) == 0

    threads = DiscourseThreadsSchema(threads=[])
    assert len(threads.threads) == 0

    sections = ContextSectionsSchema(theological_spine="spine")
    assert sections.theological_spine == "spine"
    assert isinstance(sections.genre_context, GenreContextSchema)
    assert isinstance(sections.maintenance_notes, MaintenanceNotesSchema)

    genre = GenreContextSchema(primary_genre="narrative", sub_genres=["romance"])
    assert genre.primary_genre == "narrative"

    notes = MaintenanceNotesSchema(generation_notes="auto", known_limitations=["none"])
    assert notes.generation_notes == "auto"


def test_object_schema_accepts_display_name():
    from app.models.book_context import BCDObject, VerseRef

    obj = BCDObject(
        name="פור",
        display_name="Festival of Purim",
        english_gloss="lot",
        first_appears=VerseRef(chapter=3, verse=7),
    )
    assert obj.name == "פור"
    assert obj.display_name == "Festival of Purim"

    obj_no_display = BCDObject(
        name="נעל",
        english_gloss="sandal",
        first_appears=VerseRef(chapter=4, verse=7),
    )
    assert obj_no_display.display_name == ""


def test_institution_schema_accepts_display_name():
    from app.models.book_context import BCDInstitution, VerseRef

    inst = BCDInstitution(
        name="גאל",
        display_name="Kinsman-Redemption (Go'el)",
        english_gloss="redeem",
        first_invoked=VerseRef(chapter=2, verse=20),
    )
    assert inst.name == "גאל"
    assert inst.display_name == "Kinsman-Redemption (Go'el)"

    inst_no_display = BCDInstitution(
        name="צום",
        english_gloss="fasting",
        first_invoked=VerseRef(chapter=4, verse=16),
    )
    assert inst_no_display.display_name == ""
