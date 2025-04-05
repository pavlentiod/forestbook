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
        key = f"{self.FORESTBOOK_PREFIX}:{self.prefix}:all"
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


class RedisUserStats(RedisConfig):
    def __init__(self):
        super().__init__("user-stats")

    def key_by_user_id(self, user_id: str) -> str:
        """
        Ключ для кэша по ID пользователя.
        """
        return self.one("id", user_id)

    def key_by_user_and_level(self, user_id: str, level: str) -> str:
        """
        Ключ для кэша статистики пользователя по конкретному уровню соревнований.
        """
        return f"{self.FORESTBOOK_PREFIX}:{self.prefix}:id:{user_id}:level:{level}"

    def many_by_user(self, user_id: str) -> str:
        """
        Ключ для получения всей статистики по пользователю.
        """
        return f"{self.FORESTBOOK_PREFIX}:{self.prefix}s:user:{user_id}"


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
