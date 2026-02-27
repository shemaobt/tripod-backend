import pytest

from app.core.exceptions import NotFoundError
from app.services import project_service
from tests.baker import (
    make_language,
    make_organization,
    make_organization_member,
    make_project,
    make_project_organization_access,
    make_project_user_access,
    make_user,
)


@pytest.mark.asyncio
async def test_create_project(db_session) -> None:
    lang = await make_language(db_session, code="kos")
    project = await project_service.create_project(
        db_session, name="Kokama Bible", language_id=lang.id, description="Kokama project"
    )
    assert project.name == "Kokama Bible"
    assert project.language_id == lang.id
    assert project.description == "Kokama project"


@pytest.mark.asyncio
async def test_get_project_by_id(db_session) -> None:
    lang = await make_language(db_session, code="tst")
    created = await make_project(db_session, language_id=lang.id, name="P1")
    project = await project_service.get_project_by_id(db_session, created.id)
    assert project is not None
    assert project.id == created.id


@pytest.mark.asyncio
async def test_get_project_or_404_raises_when_missing(db_session) -> None:
    with pytest.raises(NotFoundError, match="Project not found"):
        await project_service.get_project_or_404(db_session, "00000000-0000-0000-0000-000000000000")


@pytest.mark.asyncio
async def test_can_access_project_true_via_direct_user(db_session) -> None:
    user = await make_user(db_session, email="u@example.com")
    lang = await make_language(db_session, code="kos")
    project = await make_project(db_session, language_id=lang.id)
    await make_project_user_access(db_session, project.id, user.id)
    result = await project_service.can_access_project(db_session, user.id, project.id)
    assert result is True


@pytest.mark.asyncio
async def test_can_access_project_true_via_organization(db_session) -> None:
    user = await make_user(db_session, email="orguser@example.com")
    org = await make_organization(db_session, slug="org")
    await make_organization_member(db_session, user.id, org.id)
    lang = await make_language(db_session, code="kos")
    project = await make_project(db_session, language_id=lang.id)
    await make_project_organization_access(db_session, project.id, org.id)
    result = await project_service.can_access_project(db_session, user.id, project.id)
    assert result is True


@pytest.mark.asyncio
async def test_can_access_project_false(db_session) -> None:
    user = await make_user(db_session, email="nobody@example.com")
    lang = await make_language(db_session, code="kos")
    project = await make_project(db_session, language_id=lang.id)
    result = await project_service.can_access_project(db_session, user.id, project.id)
    assert result is False


@pytest.mark.asyncio
async def test_list_projects_accessible_to_user_includes_direct(db_session) -> None:
    user = await make_user(db_session, email="direct@example.com")
    lang = await make_language(db_session, code="kos")
    p1 = await make_project(db_session, language_id=lang.id, name="Alpha")
    await make_project_user_access(db_session, p1.id, user.id)
    projects = await project_service.list_projects_accessible_to_user(db_session, user.id)
    assert len(projects) == 1
    assert projects[0].id == p1.id


@pytest.mark.asyncio
async def test_list_projects_accessible_to_user_includes_via_org(db_session) -> None:
    user = await make_user(db_session, email="viaorg@example.com")
    org = await make_organization(db_session, slug="team")
    await make_organization_member(db_session, user.id, org.id)
    lang = await make_language(db_session, code="kos")
    p1 = await make_project(db_session, language_id=lang.id, name="Team Project")
    await make_project_organization_access(db_session, p1.id, org.id)
    projects = await project_service.list_projects_accessible_to_user(db_session, user.id)
    assert len(projects) == 1
    assert projects[0].id == p1.id


@pytest.mark.asyncio
async def test_list_projects_accessible_to_user_empty_when_no_access(db_session) -> None:
    user = await make_user(db_session, email="noaccess@example.com")
    lang = await make_language(db_session, code="kos")
    await make_project(db_session, language_id=lang.id, name="Other Project")
    projects = await project_service.list_projects_accessible_to_user(db_session, user.id)
    assert projects == []


@pytest.mark.asyncio
async def test_grant_user_access_creates_access(db_session) -> None:
    user = await make_user(db_session, email="grant@example.com")
    lang = await make_language(db_session, code="kos")
    project = await make_project(db_session, language_id=lang.id)
    access = await project_service.grant_user_access(db_session, project.id, user.id)
    assert access.project_id == project.id
    assert access.user_id == user.id


@pytest.mark.asyncio
async def test_grant_user_access_idempotent(db_session) -> None:
    user = await make_user(db_session, email="idem@example.com")
    lang = await make_language(db_session, code="kos")
    project = await make_project(db_session, language_id=lang.id)
    await make_project_user_access(db_session, project.id, user.id)
    access = await project_service.grant_user_access(db_session, project.id, user.id)
    assert access.project_id == project.id
    assert access.user_id == user.id


@pytest.mark.asyncio
async def test_grant_organization_access_creates_access(db_session) -> None:
    org = await make_organization(db_session, slug="new-org")
    lang = await make_language(db_session, code="kos")
    project = await make_project(db_session, language_id=lang.id)
    access = await project_service.grant_organization_access(db_session, project.id, org.id)
    assert access.project_id == project.id
    assert access.organization_id == org.id
