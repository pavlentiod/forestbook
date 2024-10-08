from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.team_member.team_member import TeamMember
from src.schemas.team_member.team_member_schema import TeamMemberOutput, TeamMemberInput, TeamMemberEndpoint


class TeamMemberRepository:
    """
    Repository for handling operations related to the TeamMember model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a database session.

        :param session: The AsyncSession to interact with the database
        """
        self.session = session

    async def add_member(self, data: TeamMemberInput) -> TeamMemberOutput:
        """
        Adds a new user to a team.

        :param data: The input data to add a user to a team
        :return: The added team member as TeamMemberOutput
        """
        team_member = TeamMember(
            user_id=data.user_id,
            team_id=data.team_id
        )
        self.session.add(team_member)
        await self.session.commit()
        await self.session.refresh(team_member)
        return TeamMemberOutput(
            id=team_member.id,
            user_id=team_member.user_id,
            team_id=team_member.team_id,
            joined_at=team_member.joined_at
        )

    async def get_all_members(self) -> List[TeamMemberOutput]:
        """
        Retrieves all team members.

        :return: A list of all team members as TeamMemberOutput
        """
        stmt = select(TeamMember).order_by(TeamMember.joined_at)
        result = await self.session.execute(stmt)
        members = result.scalars().all()
        return [TeamMemberOutput(**member.__dict__) for member in members]

    async def get_team_members(self, team_id: UUID) -> List[TeamMemberOutput]:
        """
        Retrieves all members of a specific team.

        :param team_id: The ID of the team
        :return: A list of team members for the given team as TeamMemberOutput
        """
        stmt = select(TeamMember).where(TeamMember.team_id == team_id).order_by(TeamMember.joined_at)
        result = await self.session.execute(stmt)
        members = result.scalars().all()
        return [TeamMemberOutput(**member.__dict__) for member in members]

    async def get_user_teams(self, user_id: UUID) -> List[TeamMemberOutput]:
        """
        Retrieves all teams a specific user is a member of.

        :param user_id: The ID of the user
        :return: A list of teams the user belongs to as TeamMemberOutput
        """
        stmt = select(TeamMember).where(TeamMember.user_id == user_id).order_by(TeamMember.joined_at)
        result = await self.session.execute(stmt)
        members = result.scalars().all()
        return [TeamMemberOutput(**member.__dict__) for member in members]

    async def update(self, team_member: TeamMember, data: TeamMemberEndpoint) -> TeamMemberOutput:
        """
        Updates a team member's details (e.g., changing the team).

        :param team_member: The team member instance to update
        :param data: The new data for updating the team member
        :return: The updated team member as TeamMemberOutput
        """
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(team_member, key, value)
        await self.session.commit()
        await self.session.refresh(team_member)
        return TeamMemberOutput(
            id=team_member.id,
            user_id=team_member.user_id,
            team_id=team_member.team_id,
            joined_at=team_member.joined_at
        )

    async def delete(self, team_member: TeamMember) -> bool:
        """
        Removes a user from a team.

        :param team_member: The team member to remove
        :return: True if the team member was successfully removed, otherwise False
        """
        await self.session.delete(team_member)
        await self.session.commit()
        return True

    async def team_member_exists_by_ids(self, user_id: UUID, team_id: UUID) -> bool:
        """
        Checks if a team member exists for the given user and team.

        :param user_id: The ID of the user
        :param team_id: The ID of the team
        :return: True if the team member exists, otherwise False
        """
        stmt = select(TeamMember).where(TeamMember.user_id == user_id, TeamMember.team_id == team_id)
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None
