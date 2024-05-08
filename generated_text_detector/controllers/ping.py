from fastapi import APIRouter, status
from starlette.responses import JSONResponse

router = APIRouter()

@router.get(
    "/healthcheck",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Alive method"
)
def ping():
    return JSONResponse({"healthy": True}, 200)
