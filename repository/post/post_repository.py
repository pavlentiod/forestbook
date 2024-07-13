import asyncio
from typing import List, Optional

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import db_helper
from database.models.post.post import Post
from schemas.post.post_schema import PostInput, PostOutput


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: PostInput) -> PostOutput:
        post = Post(
            title=data.title,
            place=data.place,
            median_p_bk=data.median_p_bk,
            result=data.result,
            backlog=data.backlog,
            points_number=data.points_number,
            split_firsts=data.split_firsts,
            image_path=data.image_path,
            split=data.split,
            index=data.index,
            body=data.body,
            user_id=data.user_id,
            event_id=data.event_id,
        )
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return PostOutput(
            id=post.id,
            title=post.title,
            place=post.place,
            median_p_bk=post.median_p_bk,
            result=post.result,
            backlog=post.backlog,
            points_number=post.points_number,
            split_firsts=post.split_firsts,
            image_path=post.image_path,
            split=post.split,
            index=post.index,
            body=post.body,
            created_date=post.created_date,
            user=None,  # This will be populated with user data in service layer
            event=None,  # This will be populated with event data in service layer
            gps=None  # This will be populated with GPSPostOutput in service layer
        )

    async def get_all(self) -> List[Optional[PostOutput]]:
        stmt = select(Post).order_by(Post.created_date)
        result = await self.session.execute(stmt)
        posts = result.scalars().all()
        return [PostOutput(**post.__dict__) for post in posts]

    async def get_post(self, _id: UUID4) -> PostOutput:
        post = await self.session.get(Post, _id)
        return PostOutput(**post.__dict__)

    async def get_by_id(self, _id: UUID4) -> Optional[Post]:
        return await self.session.get(Post, _id)

    async def post_exists_by_id(self, _id: UUID4) -> bool:
        post = await self.session.get(Post, _id)
        return post is not None

    async def update(self, post: Post, data: PostInput) -> PostOutput:
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(post, key, value)
        await self.session.commit()
        await self.session.refresh(post)
        return PostOutput(**post.__dict__)

    async def delete(self, post: Post) -> bool:
        await self.session.delete(post)
        await self.session.commit()
        return True


async def main():
    async with db_helper.session_factory() as session:
        ev = PostRepository(session)
        inp = PostInput(
            title="Sample Post",
            place=1,
            median_p_bk=5.0,
            result=120,
            backlog=43,
            points_number=10,
            split_firsts=2,
            image_path="/path/to/image.jpg",
            split={"point":"time"},
            index="Ivanov Pavel",
            body={"bpdy":"text"},
            event_id="e894c953-d404-4311-aea8-bc7098393157",
            user_id="2494f7df-d104-4848-a19e-7cae30960ced"
        )
        await ev.create(inp)
        # event = await ev.get_by_id("1ae075c1-aff0-4c38-acf5-0b75e25c4bc7")
        # await ev.update(event, inp2)


if __name__ == "__main__":
    asyncio.run(main())
