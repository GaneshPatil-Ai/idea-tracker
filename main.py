"""Idea Tracker — FastAPI + SQLite local-first app."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

# --- Database ---

DATABASE_URL = "sqlite:///ideas.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class StatusEnum(str, Enum):
    idea = "idea"
    research = "research"
    validate = "validate"
    build = "build"
    paused = "paused"
    killed = "killed"
    done = "done"


class IdeaModel(Base):
    __tablename__ = "ideas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    problem = Column(String(1000), nullable=True)
    opportunity = Column(String(1000), nullable=True)
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.idea, nullable=False)
    next_action = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(engine)


# --- Pydantic schemas ---

class IdeaCreate(BaseModel):
    title: str
    description: Optional[str] = None


class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    problem: Optional[str] = None
    opportunity: Optional[str] = None
    status: Optional[str] = None
    next_action: Optional[str] = None


class IdeaResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    problem: Optional[str]
    opportunity: Optional[str]
    status: str
    next_action: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- AI structuring (local, no external API) ---

def structure_idea(title: str, description: str) -> dict:
    """Heuristic-based structuring — no external API needed.

    Replace with Laya/Jev call later for AI-powered extraction.
    """
    if description:
        problem = f"Problem: {description}"
        opportunity = f"Opportunity: Building around '{title}' could unlock value by solving the above."
    else:
        problem = f"Problem: {title} addresses a gap or pain point."
        opportunity = f"Opportunity: {title} could create value by solving the above."
    return {"problem": problem, "opportunity": opportunity}


# --- FastAPI app ---

app = FastAPI(title="Idea Tracker", version="0.1.0")
templates = Jinja2Templates(directory="templates")


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
def index(request: Request, status: str = "all"):
    db = SessionLocal()
    query = db.query(IdeaModel)
    if status != "all":
        query = query.filter(IdeaModel.status == status)
    ideas = query.order_by(IdeaModel.created_at.desc()).all()
    db.close()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ideas": ideas,
        "status": status,
        "statuses": [s.value for s in StatusEnum],
    })


@app.post("/ideas/", response_class=HTMLResponse)
def create_idea(request: Request, title: str, description: str = ""):
    db = SessionLocal()
    idea = IdeaModel(title=title, description=description or None)
    db.add(idea)
    db.commit()
    db.refresh(idea)
    db.close()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ideas": [idea],
        "status": "all",
        "statuses": [s.value for s in StatusEnum],
    })


@app.post("/ideas/{idea_id}/status", response_class=HTMLResponse)
def update_status(idea_id: int, status: str, request: Request):
    db = SessionLocal()
    idea = db.get(IdeaModel, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    idea.status = status
    db.commit()
    db.refresh(idea)
    db.close()
    # Redirect back to list
    from fastapi.responses import RedirectResponse
    return RedirectResponse("/", status_code=303)


@app.post("/ideas/{idea_id}/structure", response_class=HTMLResponse)
def structure_idea_endpoint(idea_id: int, request: Request):
    db = SessionLocal()
    idea = db.get(IdeaModel, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    result = structure_idea(idea.title, idea.description or "")
    idea.problem = result["problem"]
    idea.opportunity = result["opportunity"]
    db.commit()
    db.refresh(idea)
    db.close()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "ideas": [idea],
        "status": "all",
        "statuses": [s.value for s in StatusEnum],
    })


@app.get("/api/ideas", response_model=list[IdeaResponse])
def list_ideas_api(status: Optional[str] = None):
    db = SessionLocal()
    query = db.query(IdeaModel)
    if status:
        query = query.filter(IdeaModel.status == status)
    ideas = query.order_by(IdeaModel.created_at.desc()).all()
    db.close()
    return ideas


@app.post("/api/ideas", response_model=IdeaResponse)
def create_idea_api(idea: IdeaCreate):
    db = SessionLocal()
    db_idea = IdeaModel(title=idea.title, description=idea.description)
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    db.close()
    return db_idea


@app.put("/api/ideas/{idea_id}", response_model=IdeaResponse)
def update_idea_api(idea_id: int, idea: IdeaUpdate):
    db = SessionLocal()
    db_idea = db.get(IdeaModel, idea_id)
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    for key, value in idea.model_dump(exclude_unset=True).items():
        setattr(db_idea, key, value)
    db.commit()
    db.refresh(db_idea)
    db.close()
    return db_idea


@app.delete("/api/ideas/{idea_id}")
def delete_idea_api(idea_id: int):
    db = SessionLocal()
    db_idea = db.get(IdeaModel, idea_id)
    if not db_idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    db.delete(db_idea)
    db.commit()
    db.close()
    return {"ok": True}


# --- Static files ---

app.mount("/static", StaticFiles(directory="static"), name="static")
