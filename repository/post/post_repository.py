from sqlalchemy.orm import Session
from database.models.post.post import Post
from schemas.post.post_schema import PostInput, PostOutput
from typing import List, Optional
from uuid import UUID


class PostRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: PostInput) -> PostOutput:
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
            body=data.body
        )
        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)
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
            user=post.user,
            event=post.event,
            gps=post.gps
        )

    def get_all(self) -> List[Optional[PostOutput]]:
        posts = self.session.query(Post).all()
        return [PostOutput(
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
            user=post.user,
            event=post.event,
            gps=post.gps
        ) for post in posts]

    def get_post(self, post_id: UUID) -> PostOutput:
        post = self.session.query(Post).filter_by(id=post_id).first()
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
            user=post.user,
            event=post.event,
            gps=post.gps
        )

    def get_by_id(self, post_id: UUID) -> Optional[Post]:
        return self.session.query(Post).filter_by(id=post_id).first()

    def post_exists_by_id(self, post_id: UUID) -> bool:
        post = self.session.query(Post).filter_by(id=post_id).first()
        return post is not None

    def update(self, post: Post, data: PostInput) -> PostOutput:
        post.title = data.title
        post.place = data.place
        post.median_p_bk = data.median_p_bk
        post.result = data.result
        post.backlog = data.backlog
        post.points_number = data.points_number
        post.split_firsts = data.split_firsts
        post.image_path = data.image_path
        post.split = data.split
        post.index = data.index
        post.body = data.body
        self.session.commit()
        self.session.refresh(post)
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
            user=post.user,
            event=post.event,
            gps=post.gps
        )

    def delete(self, post: Post) -> bool:
        self.session.delete(post)
        self.session.commit()
        return True
