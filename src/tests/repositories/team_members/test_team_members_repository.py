from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.team_members.team_members_repository import TeamMemberRepository
from src.schemas.team_member.team_member_schema import TeamMemberInput, TeamMemberUpdate


@pytest.mark.anyio
class TestTeamMemberRepository:
    @pytest.fixture
    async def team_member_repo(self, session: AsyncSession):
        return TeamMemberRepository(session)

    @pytest.fixture
    async def create_team_member(self, team_member_repo: TeamMemberRepository):
        team_member_data = TeamMemberInput(
            user_id=uuid4(),
            team_id=uuid4()
        )
        return await team_member_repo.add_member(team_member_data)

    async def test_add_team_member(self, team_member_repo: TeamMemberRepository):
        """Test adding a new team member."""
        team_member_data = TeamMemberInput(
            user_id=uuid4(),
            team_id=uuid4()
        )
        team_member = await team_member_repo.add_member(team_member_data)

        assert team_member.id is not None
        assert team_member.user_id == team_member_data.user_id
        assert team_member.team_id == team_member_data.team_id

    async def test_get_all_team_members(self, team_member_repo: TeamMemberRepository, create_team_member):
        """Test retrieving all team members."""
        team_member = await create_team_member
        members = await team_member_repo.get_all_members()

        assert len(members) > 0
        assert members[0].id == team_member.id

    async def test_get_team_members_by_team_id(self, team_member_repo: TeamMemberRepository, create_team_member):
        """Test retrieving members of a specific team."""
        team_member = await create_team_member
        members = await team_member_repo.get_team_members(team_member.team_id)

        assert len(members) > 0
        assert members[0].team_id == team_member.team_id

    async def test_get_user_teams(self, team_member_repo: TeamMemberRepository, create_team_member):
        """Test retrieving teams a specific user is a member of."""
        team_member = await create_team_member
        user_teams = await team_member_repo.get_user_teams(team_member.user_id)

        assert len(user_teams) > 0
        assert user_teams[0].user_id == team_member.user_id

    async def test_update_team_member(self, team_member_repo: TeamMemberRepository, create_team_member):
        """Test updating a team member's details."""
        team_member = await create_team_member
        updated_data = TeamMemberUpdate(team_id=uuid4())
        updated_team_member = await team_member_repo.update(team_member, updated_data)

        assert updated_team_member.team_id == updated_data.team_id

    async def test_delete_team_member(self, team_member_repo: TeamMemberRepository, create_team_member):
        """Test removing a team member from a team."""
        team_member = await create_team_member
        deleted = await team_member_repo.delete(team_member)

        assert deleted is True
        assert await team_member_repo.get_team_members(team_member.team_id) == []

    async def test_team_member_exists_by_ids(self, team_member_repo: TeamMemberRepository, create_team_member):
        """Test checking if a team member exists by user ID and team ID."""
        team_member = await create_team_member
        exists = await team_member_repo.team_member_exists_by_ids(team_member.user_id, team_member.team_id)

        assert exists is True

    async def test_team_member_does_not_exist(self, team_member_repo: TeamMemberRepository):
        """Test checking if a team member does not exist by non-matching user ID and team ID."""
        exists = await team_member_repo.team_member_exists_by_ids(uuid4(), uuid4())

        assert exists is False
