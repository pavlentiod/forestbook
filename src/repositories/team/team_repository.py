from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.team.team import Team
from src.schemas.team.team_schema import TeamInput, TeamOutput, TeamEndpoint


class TeamRepository:
    """
    Repository for handling operations related to the Team model.
    """

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with a database session.

        :param session: The AsyncSession to interact with the database
        """
        self.session = session

    async def create(self, data: TeamInput) -> TeamOutput:
        """
        Creates a new team and stores it in the database.

        :param data: The input data to create the team
        :return: The created team as TeamOutput
        """
        team = Team(
            name=data.name,
            description=data.description,
            owner_id=data.owner_id
        )
        self.session.add(team)
        await self.session.commit()
        await self.session.refresh(team)
        return TeamOutput(
            id=team.id,
            name=team.name,
            description=team.description,
            owner_id=team.owner_id,
            created_at=team.created_at
        )

    async def get_all(self) -> List[Optional[TeamOutput]]:
        """
        Retrieves all teams from the database, ordered by creation date.

        :return: A list of TeamOutput objects representing all teams
        """
        stmt = select(Team).order_by(Team.created_at)
        result = await self.session.execute(stmt)
        teams = result.scalars().all()
        return [TeamOutput(**team.__dict__) for team in teams]

    async def get_team(self, _id: UUID) -> TeamOutput:
        """
        Retrieves a specific team by its ID.

        :param _id: The ID of the team to retrieve
        :return: The team as TeamOutput if found, otherwise None
        """
        team = await self.session.get(Team, _id)
        if team:
            return TeamOutput(
                id=team.id,
                name=team.name,
                description=team.description,
                owner_id=team.owner_id,
                created_at=team.created_at
            )
        return None

    async def get_teams_by_owner_id(self, owner_id: UUID) -> List[TeamOutput]:
        """
        Retrieves all teams owned by a specific user (owner).

        :param owner_id: The ID of the team owner
        :return: A list of teams owned by the given user as TeamOutput
        """
        stmt = select(Team).where(Team.owner_id == owner_id).order_by(Team.created_at)
        result = await self.session.execute(stmt)
        teams = result.scalars().all()
        return [TeamOutput(**team.__dict__) for team in teams]

    async def update(self, team: Team, data: TeamEndpoint) -> TeamOutput:
        """
        Updates an existing team with the given data.

        :param team: The team instance to update
        :param data: The new data for updating the team
        :return: The updated team as TeamOutput
        """
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(team, key, value)
        await self.session.commit()
        await self.session.refresh(team)
        return TeamOutput(
            id=team.id,
            name=team.name,
            description=team.description,
            owner_id=team.owner_id,
            created_at=team.created_at
        )

    async def delete(self, team: Team) -> bool:
        """
        Deletes a team from the database.

        :param team: The team to delete
        :return: True if the team was successfully deleted, otherwise False
        """
        await self.session.delete(team)
        await self.session.commit()
        return True

    async def team_exists_by_id(self, _id: UUID) -> bool:
        """
        Checks if a team exists by its ID.

        :param _id: The ID of the team
        :return: True if the team exists, otherwise False
        """
        team = await self.session.get(Team, _id)
        return team is not None
