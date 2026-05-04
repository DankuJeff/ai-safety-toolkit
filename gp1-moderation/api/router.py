from fastapi import APIRouter, Depends, Request

from classifier.moderator import Moderator
from classifier.models import ModerationRequest, ModerationResponse

router = APIRouter(prefix="/api/v1", tags=["moderation"])


def get_moderator(request: Request) -> Moderator:
    return request.app.state.moderator


@router.post("/moderate", response_model=ModerationResponse)
def moderate(payload: ModerationRequest, moderator: Moderator = Depends(get_moderator)):
    return moderator.moderate(payload)


@router.get("/health")
def health():
    return {"status": "ok"}
