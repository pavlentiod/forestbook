from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.team.team_repository import TeamRepository
from src.schemas.team.team_schema import TeamInput, TeamUpdate


@pytest.mark.anyio
class TestTeamRepository:
    @pytest.fixture
    async def team_repo(self, session: AsyncSession):
        return TeamRepository(session)

    @pytest.fixture
    async def create_team(self, team_repo: TeamRepository):
        team_data = TeamInput(
            name="Test Team",
            description="A test team",
            owner_id=uuid4()
        )
        return await team_repo.create(team_data)

    async def test_create_team(self, team_repo: TeamRepository):
        """Test creating a team."""
        team_data = TeamInput(
            name="New Team",
            description="A new team for testing",
            owner_id=uuid4()
        )
        team = await team_repo.create(team_data)

        assert team.id is not None
        assert team.name == "New Team"
        assert team.description == "A new team for testing"
        assert team.owner_id is not None

    async def test_get_all_teams(self, team_repo: TeamRepository, create_team):
        """Test retrieving all teams."""
        team = await create_team
        teams = await team_repo.get_all()

        assert len(teams) > 0
        assert teams[0].id == team.id

    async def test_get_team_by_id(self, team_repo: TeamRepository, create_team):
        """Test retrieving a team by its ID."""
        team = await create_team
        retrieved_team = await team_repo.get_team(team.id)

        assert retrieved_team.id == team.id
        assert retrieved_team.name == team.name

    async def test_get_teams_by_owner_id(self, team_repo: TeamRepository, create_team):
        """Test retrieving all teams owned by a specific user."""
        team = await create_team
        teams = await team_repo.get_teams_by_owner_id(team.owner_id)

        assert len(teams) > 0
        assert teams[0].owner_id == team.owner_id

    async def test_update_team(self, team_repo: TeamRepository, create_team):
        """Test updating a team."""
        team = await create_team
        updated_data = TeamUpdate(name="Updated Team Name", description="Updated description")
        updated_team = await team_repo.update(team, updated_data)

        assert updated_team.name == "Updated Team Name"
        assert updated_team.description == "Updated description"

    async def test_delete_team(self, team_repo: TeamRepository, create_team):
        """Test deleting a team."""
        team = await create_team
        deleted = await team_repo.delete(team)

        assert deleted is True
        assert await team_repo.get_team(team.id) is None

    async def test_team_exists_by_id(self, team_repo: TeamRepository, create_team):
        """Test checking if a team exists by ID."""
        team = await create_team
        exists = await team_repo.team_exists_by_id(team.id)

        assert exists is True

    async def test_team_does_not_exist(self, team_repo: TeamRepository):
        """Test checking if a team does not exist by an invalid ID."""
        exists = await team_repo.team_exists_by_id(uuid4())

        assert exists is False
