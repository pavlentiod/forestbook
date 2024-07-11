from sqlalchemy.orm import Session
from database.models.post.gps_post import GPS_Post
from schemas.post.gps_post_schema import GPSPostInput, GPSPostOutput
from typing import List, Optional
from uuid import UUID


class GPSPostRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: GPSPostInput) -> GPSPostOutput:
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
        self.session.commit()
        self.session.refresh(gps_post)
        return GPSPostOutput(
            id=gps_post.id,
            lenght_s=gps_post.lenght_s,
            lenght_p=gps_post.lenght_p,
            climb=gps_post.climb,
            pace=gps_post.pace,
            gpx_path=gps_post.gpx_path,
            coord_data=gps_post.coord_data,
            post=None  # Assuming post relationship is not populated here
        )

    def get_all(self) -> List[Optional[GPSPostOutput]]:
        gps_posts = self.session.query(GPS_Post).all()
        return [GPSPostOutput(
            id=gps_post.id,
            lenght_s=gps_post.lenght_s,
            lenght_p=gps_post.lenght_p,
            climb=gps_post.climb,
            pace=gps_post.pace,
            gpx_path=gps_post.gpx_path,
            coord_data=gps_post.coord_data,
            post=gps_post.post
        ) for gps_post in gps_posts]

    def get_gps_post(self, gps_post_id: UUID) -> GPSPostOutput:
        gps_post = self.session.query(GPS_Post).filter_by(id=gps_post_id).first()
        return GPSPostOutput(
            id=gps_post.id,
            lenght_s=gps_post.lenght_s,
            lenght_p=gps_post.lenght_p,
            climb=gps_post.climb,
            pace=gps_post.pace,
            gpx_path=gps_post.gpx_path,
            coord_data=gps_post.coord_data,
            post=gps_post.post
        )

    def get_by_id(self, gps_post_id: UUID) -> Optional[GPS_Post]:
        return self.session.query(GPS_Post).filter_by(id=gps_post_id).first()

    def gps_post_exists_by_id(self, gps_post_id: UUID) -> bool:
        gps_post = self.session.query(GPS_Post).filter_by(id=gps_post_id).first()
        return gps_post is not None

    def update(self, gps_post: GPS_Post, data: GPSPostInput) -> GPSPostOutput:
        gps_post.lenght_s = data.lenght_s
        gps_post.lenght_p = data.lenght_p
        gps_post.climb = data.climb
        gps_post.pace = data.pace
        gps_post.gpx_path = data.gpx_path
        gps_post.coord_data = data.coord_data
        self.session.commit()
        self.session.refresh(gps_post)
        return GPSPostOutput(
            id=gps_post.id,
            lenght_s=gps_post.lenght_s,
            lenght_p=gps_post.lenght_p,
            climb=gps_post.climb,
            pace=gps_post.pace,
            gpx_path=gps_post.gpx_path,
            coord_data=gps_post.coord_data,
            post=gps_post.post
        )

    def delete(self, gps_post: GPS_Post) -> bool:
        self.session.delete(gps_post)
        self.session.commit()
        return True
