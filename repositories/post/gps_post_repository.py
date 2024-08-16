import asyncio
from typing import List, Optional

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import db_helper
from database.models.post.gps_post import GPS_Post
from schemas.post.gps_post_schema import GPSPostInput, GPSPostOutput


class GPSPostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: GPSPostInput) -> GPSPostOutput:
        gps_post = GPS_Post(
            lenght_s=data.lenght_s,
            lenght_p=data.lenght_p,
            climb=data.climb,
            pace=data.pace,
            gpx_path=data.gpx_path,
            coord_data=data.coord_data,
            post_id=data.post_id
        )
        self.session.add(gps_post)
        await self.session.commit()
        await self.session.refresh(gps_post)
        return GPSPostOutput(
            id=gps_post.id,
            lenght_s=gps_post.lenght_s,
            lenght_p=gps_post.lenght_p,
            climb=gps_post.climb,
            pace=gps_post.pace,
            gpx_path=gps_post.gpx_path,
            coord_data=gps_post.coord_data,
            post_id=gps_post.post_id
        )

    async def get_all(self) -> List[Optional[GPSPostOutput]]:
        stmt = select(GPS_Post).order_by(GPS_Post.id)
        result = await self.session.execute(stmt)
        gps_posts = result.scalars().all()
        return [GPSPostOutput(**gps_post.__dict__) for gps_post in gps_posts]

    async def get_gps_post(self, _id: UUID4) -> GPSPostOutput:
        gps_post = await self.session.get(GPS_Post, _id)
        return GPSPostOutput(**gps_post.__dict__)

    async def get_by_id(self, _id: UUID4) -> Optional[GPS_Post]:
        return await self.session.get(GPS_Post, _id)

    async def gps_post_exists_by_id(self, _id: UUID4) -> bool:
        gps_post = await self.session.get(GPS_Post, _id)
        return gps_post is not None

    async def update(self, gps_post: GPS_Post, data: GPSPostInput) -> GPSPostOutput:
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(gps_post, key, value)
        await self.session.commit()
        await self.session.refresh(gps_post)
        return GPSPostOutput(**gps_post.__dict__)

    async def delete(self, gps_post: GPS_Post) -> bool:
        await self.session.delete(gps_post)
        await self.session.commit()
        return True


# async def main():
#     async with db_helper.session_factory() as session:
#         ev = GPSPostRepository(session)
#         inp = GPSPostInput(
#             lenght_s=10.5,
#             lenght_p=20.3,
#             climb=300,
#             pace="5:30",
#             gpx_path="/path/to/gpx",
#             coord_data="some coordinates",
#             post_id=
#         )
#         await ev.create(inp)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
