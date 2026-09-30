from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.llm.recovery_agent import run_recovery_agent


router = APIRouter(
    prefix="/api/agent",
    tags=["Recovery Agent"],
)


@router.post("/recovery/{recovery_case_id}")
def run_agent(
    recovery_case_id: int,
    db: Session = Depends(get_db),
):
    return run_recovery_agent(
        db=db,
        recovery_case_id=recovery_case_id,
    )