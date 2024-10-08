from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

# Schema for input data (adding a user to a team)
class TeamMemberInput(BaseModel):
    user_id: UUID
    team_id: UUID

# Schema for output data (displaying a team member)
class TeamMemberOutput(BaseModel):
    id: UUID
    user_id: UUID
    team_id: UUID
    joined_at: datetime

# Schema for endpoints (updating a team member, e.g., changing the team)
class TeamMemberEndpoint(BaseModel):
    user_id: UUID
    team_id: UUID
