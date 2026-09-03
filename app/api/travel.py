from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.services.travel_service import (
    run_travel_agent,
    resume_travel_agent,
)
from app.core.logging import get_logger


logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/travel",
    tags=["Travel"]
)


class TravelRequest(BaseModel):

    message: str = Field(
        min_length=1,
        max_length=5000
    )

    thread_id: str | None = None


class ApprovalRequest(BaseModel):

    thread_id: str = Field(
        min_length=1
    )

    approved: bool

    feedback: str = Field(
        default="",
        max_length=3000
    )


@router.post("")
async def travel_planner(
    request: TravelRequest
):

    logger.info(
        "Travel API request received"
    )

    try:

        result = run_travel_agent(
            user_input=request.message,
            thread_id=request.thread_id
        )

        return {
            "success": True,
            **result
        }

    except Exception:

        logger.exception(
            "Travel API failed"
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": (
                    "Unable to process "
                    "travel request."
                )
            }
        )


@router.post("/approve")
async def approve_travel_plan(
    request: ApprovalRequest
):

    try:

        result = resume_travel_agent(
            thread_id=request.thread_id,
            approved=request.approved,
            feedback=request.feedback
        )

        return {
            "success": True,
            **result
        }

    except Exception:

        logger.exception(
            "Travel approval API failed"
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": (
                    "Unable to resume "
                    "travel workflow."
                )
            }
        )