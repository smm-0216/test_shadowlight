from fastapi import APIRouter, HTTPException

from utils.agent import Agent
from utils.database import Database
from schemas.agent import AskRequest, AskResponse

router = APIRouter(prefix="/ask", tags=["ask"])


@router.post("/", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        agent = Agent()
        db = Database()

        question = request.question
        query = agent.generate_sql(question)

        data = db.read_sql(query)
        if data is None:
            raise HTTPException(
                status_code=500,
                detail="Database error."
            )
        if data.empty:
            return AskResponse(
                question=request.question,
                answer="No data found for your question."
            )

        return AskResponse(
            question=request.question,
            answer=data.to_dict(orient="records")
        )
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error while fetching an answer."
        )
