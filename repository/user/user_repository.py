from sqlalchemy.orm import Session
from database.models.user.user import User
from schemas.user.user_schema import UserInput, UserOutput
from typing import List, Optional
from pydantic import UUID4


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: UserInput) -> UserOutput:
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            hashed_password=b'',  # You should hash the password before saving it
            access=data.access,
            is_active=data.is_active,
            email=data.email
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return UserOutput(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            access=user.access,
            is_active=user.is_active,
            posts=[]
        )

    def get_all(self) -> List[Optional[UserOutput]]:
        users = self.session.query(User).all()
        return [UserOutput(**user.__dict__) for user in users]

    def get_user(self, user_id: UUID4) -> UserOutput:
        user = self.session.query(User).filter_by(id=user_id).first()
        return UserOutput(**user.__dict__)

    def get_by_id(self, user_id: UUID4) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()

    def user_exists_by_id(self, user_id: UUID4) -> bool:
        user = self.session.query(User).filter_by(id=user_id).first()
        return user is not None

    def user_exists_by_email(self, email: str) -> bool:
        user = self.session.query(User).filter_by(email=email).first()
        return user is not None

    def update(self, user: User, data: UserInput) -> UserOutput:
        user.first_name = data.first_name
        user.last_name = data.last_name
        user.access = data.access
        user.is_active = data.is_active
        user.email = data.email
        self.session.commit()
        self.session.refresh(user)
        return UserOutput(**user.__dict__)

    def delete(self, user: User) -> bool:
        self.session.delete(user)
        self.session.commit()
        return True
