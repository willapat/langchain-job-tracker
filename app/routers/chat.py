from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.schemas import ChatRequest, ResumeRequest
from app.services.agent_runtime import get_thread_state, stream_chat, stream_resume

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat(payload: ChatRequest):
    return EventSourceResponse(stream_chat(payload.message, payload.thread_id))


@router.post("/resume")
async def resume(payload: ResumeRequest):
    decisions = [d.model_dump(exclude_none=True) for d in payload.decisions]
    return EventSourceResponse(stream_resume(decisions, payload.thread_id))


@router.get("/{thread_id}/state")
async def thread_state(thread_id: str):
    return await get_thread_state(thread_id)
