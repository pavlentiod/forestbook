from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from src.config.modules.scopes_config import ScopesConfig

scopes = ScopesConfig()


class Route(BaseModel):
    path: str
    full_path: str = ""
    security: Optional[list[str]] = []


class PrefixedRouter(BaseSettings):
    prefix: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for field in self.model_fields:
            route = getattr(self, field)
            if isinstance(route, Route):
                route.full_path = self.prefix + route.path


class UserRouter(PrefixedRouter):
    prefix: str = "/users"
    create: Route = Route(path="/", security=[scopes.user_profile_update.value])
    delete: Route = Route(path="/{_id}", security=[scopes.user_manage.value])
    read: Route = Route(path="/{_id}", security=[scopes.user_manage.value])  # Admin access to any profile
    update: Route = Route(path="/{_id}", security=[scopes.user_manage.value])  # Admin updates any profile
    get_by_email: Route = Route(path="/", security=[scopes.user_manage.value])
    get_all: Route = Route(path="/", security=[scopes.user_manage.value])


class PostRouter(PrefixedRouter):
    prefix: str = "/posts"
    create: Route = Route(path="/", security=[scopes.posts_write.value])
    delete: Route = Route(path="/{_id}", security=[scopes.posts_delete.value])
    read: Route = Route(path="/{_id}", security=[scopes.posts_read.value])
    update: Route = Route(path="/{_id}", security=[scopes.posts_write.value])
    get_all: Route = Route(path="/", security=[scopes.posts_read.value])


class AuthRouter(PrefixedRouter):
    prefix: str = ""
    login: Route = Route(path="/login", security=[])  # Open to all users
    refresh: Route = Route(path="/refresh", security=[])  # Requires valid refresh token


class PostStorageRouter(PrefixedRouter):
    prefix: str = "/s3/posts"
    delete: Route = Route(path="/{_id}/{key}", security=[scopes.posts_delete.value])
    upload: Route = Route(path="/{key}", security=[scopes.posts_write.value])
    download: Route = Route(path="/{_id}/{key}", security=[scopes.posts_read.value])
    get_all: Route = Route(path="/{_id}", security=[scopes.posts_read.value])


class SessionRouter(PrefixedRouter):
    prefix: str = "/c"
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
    # получить текущую активную подписку
    get_user_subscription: Route = Route(
        path="/subscription",
        security=[scopes.user_profile_read.value]
    )


class SubscriptionRouter(PrefixedRouter):
    prefix: str = "/subscriptions"
    # публичный просмотр активных планов
    get_all_plans: Route = Route(path="/plans/", security=[])

    # оформить подписку
    subscribe: Route = Route(
        path="/",
        security=[scopes.user_profile_update.value]
    )

    # --- Админ-функции по планам ---
    create_plan: Route = Route(
        path="/plans/",
        security=[scopes.user_manage.value]
    )

    update_plan: Route = Route(
        path="/plans/{_id}",
        security=[scopes.user_manage.value]
    )

    delete_plan: Route = Route(
        path="/plans/{_id}",
        security=[scopes.user_manage.value]
    )
