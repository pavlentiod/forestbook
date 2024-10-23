from fastapi import APIRouter

from src.routers.user.user import user_router

router = APIRouter()

router.include_router(user_router, prefix="/users", tags=['Users'])

# TODO: Post.tic_01  Add filters to get_all request
# TODO: Team.tic_01  Add filters to get_all request
# TODO: Team_member.tic_01  Add filters to get_all request
# TODO: User.tic_01  Add filters to get_all request