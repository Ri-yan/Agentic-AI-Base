# analytics_platform/api/routes.py

from fastapi import APIRouter
from core.models.agent_payload import AgentQuery
from services.agent_executor import run_agent_query
from usecases.agpt_generation.advance_analytics_usecase import AdvanceAnalyticsUseCase

router = APIRouter()

@router.post("/agentic/chat")
async def run_agent(payload: AgentQuery):
    result = await run_agent_query(session_id= payload.sessionId, prompt=payload.prompt,payload=payload.payload)
    return result

@router.post("/genai/run")
async def run_genai(payload: dict):
    result = await AdvanceAnalyticsUseCase().execute(prompt=payload)
    return result
