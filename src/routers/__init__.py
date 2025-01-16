from fastapi import APIRouter

from src.routers.user.user_router import router as user_router
from src.routers.auth.auth_router import router as auth_router
from src.routers.post.post_router import router as post_router
from src.routers.storage.post_storage_router import router as post_storage_router
from src.routers.session.session_router import router as session_router

router = APIRouter()

router.include_router(session_router, prefix="/c", tags=['Current session'])
router.include_router(user_router, prefix="/users", tags=['Users'])
router.include_router(post_router, prefix="/posts", tags=['Posts'])
router.include_router(post_storage_router, prefix="/s3/posts", tags=['Post Storage'])
router.include_router(auth_router, prefix="", tags=['Auth'])



# TODO: Auth.tic_07  