from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from src.config.modules.scopes_config import ScopesConfig

scopes = ScopesConfig()


class Route(BaseModel):
    path: str
    security: Optional[list[str]] = []


class UserRouter(BaseSettings):
    create: Route = Route(path="/", security=[scopes.user_profile_update.value])
    delete: Route = Route(path="/{_id}", security=[scopes.user_manage.value])
    read: Route = Route(path="/{_id}", security=[scopes.user_manage.value])  # Admin access to any profile
    update: Route = Route(path="/{_id}", security=[scopes.user_manage.value])  # Admin updates any profile
    get_by_email: Route = Route(path="/email/{email}", security=[scopes.user_manage.value])
    get_all: Route = Route(path="/", security=[scopes.user_manage.value])


class PostRouter(BaseSettings):
    create: Route = Route(path="/", security=[scopes.posts_write.value])
    delete: Route = Route(path="/{_id}", security=[scopes.posts_delete.value])
    read: Route = Route(path="/{_id}", security=[scopes.posts_read.value])
    update: Route = Route(path="/{_id}", security=[scopes.posts_write.value])
    get_all: Route = Route(path="/", security=[scopes.posts_read.value])


class AuthRouter(BaseSettings):
    login: Route = Route(path="/login", security=[])  # Open to all users
    refresh: Route = Route(path="/refresh", security=[])  # Requires valid refresh token


class PostStorageRouter(BaseSettings):
    delete: Route = Route(path="/{_id}/{key}", security=[scopes.posts_delete.value])
    upload: Route = Route(path="/{key}", security=[scopes.posts_write.value])
    download: Route = Route(path="/{_id}/{key}", security=[scopes.posts_read.value])
    get_all: Route = Route(path="/{_id}", security=[scopes.posts_read.value])


class SessionRouter(BaseSettings):
    user: Route = Route(
        path="/user",
        security=[scopes.user_profile_update.value, scopes.user_profile_read.value]
    )
    posts: Route = Route(
        path="/posts",
        security=[
            scopes.posts_write.value,
            scopes.posts_read.value,
            scopes.posts_delete.value
        ]
    )
    stats: Route = Route(path="/stat", security=[])
