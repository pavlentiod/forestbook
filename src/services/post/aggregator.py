from src.clients.forestlab_client import ForestLabClient
from src.schemas.post.post_schema import PostInDB, PostExtendedResponse


class PostAggregator:
    def __init__(self, forestlab: ForestLabClient):
        self.forestlab = forestlab

    async def aggregate(self, post: PostInDB) -> PostExtendedResponse:
        """
        Обогащает пост данными из ForestLab (результаты, сплиты, гео).
        """
        async with self.forestlab as client:
            # event_info = await client.get_event(post.event_id)
            runner_stats = await client.get_runner_stat(post.event_id, post.runner_id)
            runner_info = await client.get_runner_output(post.event_id, post.runner_id)

        return PostExtendedResponse(**post.model_dump(),
                                    stats=runner_stats,
                                    info=runner_info,
                                    media=post.media
                                    )
