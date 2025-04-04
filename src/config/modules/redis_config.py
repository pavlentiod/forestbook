from urllib.parse import urlencode

from pydantic import BaseModel


class RedisConfig:
    GET_ALL_EX = 1800  # Expiration time for get_all requests
    FORESTBOOK_PREFIX = "forestbook"

    def __init__(self, prefix: str):
        self.prefix = prefix

    def one(self, key: str, value: str):
        return f"{self.FORESTBOOK_PREFIX}:{self.prefix}:{key}:{value}"

    def many(self, filters: BaseModel = None):
        # TODO: Связанные ключи в кэше
        key = f"{self.FORESTBOOK_PREFIX}:{self.prefix}s:all"
        if not filters:
            return key
        return f"{key}:{urlencode(filters.model_dump(exclude_none=True))}"


class RedisUser(RedisConfig):

    def __init__(self):
        super().__init__("user")

    def key_by_user_id(self, id: str):
        return f"{self.one('id', id)}"

    def key_by_user_email(self, email: str):
        return f"{self.one('email', email)}"


class RedisPost(RedisConfig):
    def __init__(self):
        super().__init__("post")

    def key_by_post_id(self, id: str):
        return f"{self.one('id', id)}"


class RedisAws(RedisConfig):
    def __init__(self):
        super().__init__("s3")

    def key_by_filepath(self, filepath: str):
        return f"{self.one('path', filepath)}"
