import pytest

from app.core.exceptions import ConflictError, NotFoundError
from app.services import organization_service
from tests.baker import make_organization, make_organization_member, make_user


@pytest.mark.asyncio
async def test_create_organization(db_session) -> None:
    org = await organization_service.create_organization(
        db_session, name="Acme Corp", slug="acme-corp"
    )
    assert org.name == "Acme Corp"
    assert org.slug == "acme-corp"


@pytest.mark.asyncio
async def test_create_organization_lowercases_slug(db_session) -> None:
    org = await organization_service.create_organization(db_session, name="Test", slug="UPPER-SLUG")
    assert org.slug == "upper-slug"


@pytest.mark.asyncio
async def test_create_organization_raises_conflict_when_slug_exists(db_session) -> None:
    await make_organization(db_session, slug="taken")
    with pytest.raises(ConflictError, match="slug already exists"):
        await organization_service.create_organization(db_session, name="Other", slug="taken")


@pytest.mark.asyncio
async def test_get_organization_by_id(db_session) -> None:
    created = await make_organization(db_session, slug="my-org")
    org = await organization_service.get_organization_by_id(db_session, created.id)
    assert org is not None
    assert org.id == created.id


@pytest.mark.asyncio
async def test_get_organization_by_slug(db_session) -> None:
    await make_organization(db_session, slug="find-me")
    org = await organization_service.get_organization_by_slug(db_session, "find-me")
    assert org is not None
    assert org.slug == "find-me"


@pytest.mark.asyncio
async def test_get_organization_or_404_raises_when_missing(db_session) -> None:
    with pytest.raises(NotFoundError, match="Organization not found"):
        await organization_service.get_organization_or_404(
            db_session, "00000000-0000-0000-0000-000000000000"
        )


@pytest.mark.asyncio
async def test_add_member(db_session) -> None:
    user = await make_user(db_session, email="member@example.com")
    org = await make_organization(db_session, slug="org1")
    member = await organization_service.add_member(db_session, org.id, user.id, role="member")
    assert member.user_id == user.id
    assert member.organization_id == org.id
    assert member.role == "member"


@pytest.mark.asyncio
async def test_add_member_raises_conflict_when_already_member(db_session) -> None:
    user = await make_user(db_session, email="dup@example.com")
    org = await make_organization(db_session, slug="org2")
    await make_organization_member(db_session, user.id, org.id)
    with pytest.raises(ConflictError, match="already a member"):
        await organization_service.add_member(db_session, org.id, user.id)


@pytest.mark.asyncio
async def test_is_member_true(db_session) -> None:
    user = await make_user(db_session, email="in@example.com")
    org = await make_organization(db_session, slug="org3")
    await make_organization_member(db_session, user.id, org.id)
    result = await organization_service.is_member(db_session, user.id, org.id)
    assert result is True


@pytest.mark.asyncio
async def test_is_member_false(db_session) -> None:
    user = await make_user(db_session, email="out@example.com")
    org = await make_organization(db_session, slug="org4")
    result = await organization_service.is_member(db_session, user.id, org.id)
    assert result is False
