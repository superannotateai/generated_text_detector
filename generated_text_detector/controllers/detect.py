from fastapi import APIRouter, Request, status
from starlette.responses import JSONResponse

from generated_text_detector.controllers.schemas_type import ReportResponse, TextRequest

router = APIRouter()

@router.post(
    "/detect",
    status_code=status.HTTP_200_OK,
    description="Detect generated-text report. Return dict with score and final predict"
)
async def detect(request: TextRequest, meta: Request) -> ReportResponse:
    current_app = meta.app
    detector = current_app.detector
    text = request.text
    result = detector.detect_report(text)
    return JSONResponse(result, 200)
