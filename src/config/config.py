import os
from pathlib import Path

import redis
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from pydantic_settings import BaseSettings

# load_dotenv()
from src.config.modules.aws_config import AwsTree
from src.config.modules.redis_config import RedisUser, RedisPost, RedisAws
from src.config.modules.routers_config import UserRouter, PostRouter, AuthRouter, PostStorageRouter, SessionRouter, \
    SubscriptionRouter
from src.config.modules.scopes_config import ScopesConfig

BASE_DIR = Path(__file__).parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env-dev")


class DbSettings(BaseModel):
    username: str = os.getenv("DATABASE_USER")
    password: str = os.getenv("DATABASE_PASSWORD")
    host: str = os.getenv("DATABASE_HOST")
    name: str = os.getenv("DATABASE_NAME")
    echo: bool = False

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}/{self.name}"


class RedisSettings(BaseSettings):
    port: int = 6379
    host: str = "localhost"
    user: RedisUser = RedisUser()
    post: RedisPost = RedisPost()
    storage: RedisAws = RedisAws()

    @property
    def redis_connection_pool(self):
        return redis.ConnectionPool(
            host=self.host,
            port=self.port,
            # db=0,
            # decode_responses=True
        )


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR.parent / os.getenv("JWT_PRIVATE_KEY_PATH")
    public_key_path: Path = BASE_DIR.parent / os.getenv("JWT_PUBLIC_KEY_PATH")
    algorithm: str = os.getenv("JWT_ALGORITHM")
    access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES"))
    refresh_token_expire_days: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS"))


class ApiEndpoints(BaseSettings):
    user: UserRouter = UserRouter()
    post: PostRouter = PostRouter()
    auth: AuthRouter = AuthRouter()
    session: SessionRouter = SessionRouter()
    storage: PostStorageRouter = PostStorageRouter()
    subscription: SubscriptionRouter = SubscriptionRouter()


class AWS_Settings(BaseSettings):
    AWS_DEFAULT_REGION: str = os.getenv("AWS_DEFAULT_REGION")
    AWS_BUCKET_NAME: str = os.getenv("AWS_BUCKET_NAME")
    APP_DATA: str = os.getenv("APP_PATH")
    USERS_FOLDER: str = os.getenv("USERS_PATH")
    POSTS_FOLDER: str = os.getenv("POSTS_PATH")

    @property
    def tree(self):
        return AwsTree(self.APP_DATA, self.USERS_FOLDER, self.POSTS_FOLDER)


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWT = AuthJWT()
    aws: AWS_Settings = AWS_Settings()
    scopes_config: ScopesConfig = ScopesConfig()
    api: ApiEndpoints = ApiEndpoints()
    redis: RedisSettings = RedisSettings()

    @property
    def oauth2_scheme(self) -> OAuth2PasswordBearer:
        return OAuth2PasswordBearer(tokenUrl=self.api.auth.login.path, scopes=self.scopes_config.scopes)


settings = Settings()
