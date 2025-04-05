from pathlib import Path
import redis
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from forest_config.loader import load_global_config, load_services_config, ServiceConfig
from src.config.modules.aws_config import AwsTree
from src.config.modules.redis_config import RedisUser, RedisPost, RedisAws, RedisUserStats
from src.config.modules.routers_config import (
    UserRouter, PostRouter, AuthRouter, PostStorageRouter, SessionRouter, SubscriptionRouter, UserStatsRouter
)
from src.config.modules.scopes_config import ScopesConfig

BASE_DIR = Path(__file__).resolve().parent.parent
global_config = load_global_config()
service_config = load_services_config()



class DbSettings(BaseModel):
    username: str = global_config.database.forestbook.user
    password: str = global_config.database.forestbook.password
    host: str = global_config.database.forestbook.host
    name: str = global_config.database.forestbook.name
    echo: bool = global_config.database.forestbook.echo

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}/{self.name}"


class RedisSettings(BaseSettings):
    port: int = global_config.redis.port
    host: str = global_config.redis.host
    user: RedisUser = RedisUser()
    user_stats: RedisUserStats = RedisUserStats()
    post: RedisPost = RedisPost()
    storage: RedisAws = RedisAws()

    @property
    def redis_connection_pool(self):
        return redis.ConnectionPool(host=self.host, port=self.port)


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR.parent / global_config.jwt.private_key_path
    public_key_path: Path = BASE_DIR.parent / global_config.jwt.public_key_path
    algorithm: str = global_config.jwt.algorithm
    access_token_expire_minutes: int = global_config.jwt.access_token_expire_minutes
    refresh_token_expire_days: int = global_config.jwt.refresh_token_expire_days


class S3Settings(BaseSettings):
    region: str = global_config.s3.region
    bucket: str = global_config.s3.bucket
    app_path: str = global_config.s3.app_path
    users_folder: str = global_config.s3.users_path
    posts_folder: str = global_config.s3.posts_path
    access_key: str = global_config.s3.access_key
    secret_key: str = global_config.s3.secret_key

    @property
    def tree(self):
        return AwsTree(self.app_path, self.users_folder, self.posts_folder)


class ApiEndpoints(BaseSettings):
    user: UserRouter = UserRouter()
    user_stats: UserStatsRouter = UserStatsRouter()
    post: PostRouter = PostRouter()
    auth: AuthRouter = AuthRouter()
    session: SessionRouter = SessionRouter()
    storage: PostStorageRouter = PostStorageRouter()
    subscription: SubscriptionRouter = SubscriptionRouter()

class ServicesSettings(BaseSettings):
    forestlab: ServiceConfig = service_config.forestlab
    forestbook: ServiceConfig = service_config.forestbook

class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWT = AuthJWT()
    aws: S3Settings = S3Settings()
    scopes_config: ScopesConfig = ScopesConfig()
    api: ApiEndpoints = ApiEndpoints()
    redis: RedisSettings = RedisSettings()
    services: ServicesSettings = ServicesSettings()

    @property
    def oauth2_scheme(self) -> OAuth2PasswordBearer:
        return OAuth2PasswordBearer(tokenUrl=self.api.auth.login.path, scopes=self.scopes_config.scopes)


settings = Settings()
