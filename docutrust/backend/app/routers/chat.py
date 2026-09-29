import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.responses import Response

from app.auth.dependencies import get_current_user, get_user_from_token
from app.database.mongo import get_database
from app.schemas.chat import AgentLog, ChatRequest, ChatResponse, FavoriteRequest
from app.services.chat_service import ChatService
from app.services.websocket_manager import manager


router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, current_user: dict = Depends(get_current_user)) -> ChatResponse:
    service = ChatService(get_database())
    return await service.answer_question(user=current_user, request=payload)


@router.get("/history", response_model=list[ChatResponse])
async def history(current_user: dict = Depends(get_current_user), limit: int = 25) -> list[ChatResponse]:
    service = ChatService(get_database())
    return await service.list_history(user=current_user, limit=min(max(limit, 1), 100))


@router.get("/history/{chat_id}/export")
async def export_history(chat_id: str, current_user: dict = Depends(get_current_user)) -> Response:
    service = ChatService(get_database())
    content = await service.export_pdf(user=current_user, chat_id=chat_id)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="docutrust-chat-{chat_id}.pdf"'},
    )


@router.patch("/history/{chat_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def favorite_history(
    chat_id: str,
    payload: FavoriteRequest,
    current_user: dict = Depends(get_current_user),
) -> None:
    service = ChatService(get_database())
    await service.toggle_favorite(user=current_user, chat_id=chat_id, favorite=payload.favorite)


@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    user = await get_user_from_token(token or "")
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)
    service = ChatService(get_database())

    async def emit(log: AgentLog) -> None:
        await manager.send_json(websocket, {"type": "agent_log", "payload": log.model_dump(mode="json")})

    try:
        while True:
            payload = await websocket.receive_json()
            request = ChatRequest(**payload)
            response = await service.answer_question(user=user, request=request, emit=emit)
            for word in response.answer.split():
                await manager.send_json(websocket, {"type": "answer_chunk", "payload": {"content": f"{word} "}})
                await asyncio.sleep(0.008)
            await manager.send_json(websocket, {"type": "final_answer", "payload": response.model_dump(mode="json")})
    except WebSocketDisconnect:
        return
