from typing import Dict, List
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Scope(BaseModel):
    """
    Represents a single application scope with its value and description.
    """
    value: str
    description: str


class ScopesConfig(BaseSettings):
    """
    Configuration class for managing application scopes and role-based access.
    """
    posts_read: Scope = Scope(value="posts:read", description="Permission to read posts.")
    posts_write: Scope = Scope(value="posts:write", description="Permission to create and edit posts.")
    posts_delete: Scope = Scope(value="posts:delete", description="Permission to delete posts.")
    events_read: Scope = Scope(value="events:read", description="Permission to read events.")
    events_write: Scope = Scope(value="events:write", description="Permission to create and edit events.")
    events_delete: Scope = Scope(value="events:delete", description="Permission to delete events.")
    user_profile_read: Scope = Scope(value="user:profile:read", description="Permission to read own profile information.")
    user_profile_update: Scope = Scope(value="user:profile:update", description="Permission to update own profile information.")
    user_manage: Scope = Scope(value="user:manage", description="Permission to manage users and their roles (admin only).")

    @property
    def scopes(self) -> Dict[str, str]:
        """
        Returns a dictionary of all scopes with their descriptions.
        """
        vals = list(self.model_dump().values())
        return {v["value"]: v["description"] for v in vals}

    @property
    def role_scopes(self) -> Dict[str, List[str]]:
        """
        Returns a dictionary where keys represent roles and values are lists of scope values assigned to each role.
        """
        return {
            "user": [
                self.posts_read.value,
                self.posts_write.value,
                self.posts_delete.value,
                self.events_read.value,
                self.user_profile_read.value,
                self.user_profile_update.value,
            ],
            "manager": [
                self.posts_read.value,
                self.posts_write.value,
                self.posts_delete.value,
                self.events_read.value,
                self.events_write.value,
                self.events_delete.value,
                self.user_profile_read.value,
                self.user_profile_update.value,
            ],
            "admin": [
                self.posts_read.value,
                self.posts_write.value,
                self.posts_delete.value,
                self.events_read.value,
                self.events_write.value,
                self.events_delete.value,
                self.user_profile_read.value,
                self.user_profile_update.value,
                self.user_manage.value,
            ],
        }
