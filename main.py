from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------- DB ----------
DATABASE_URL = "sqlite:///./incidents.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Status(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class Source(str, Enum):
    operator = "operator"
    monitoring = "monitoring"
    partner = "partner"

class IncidentORM(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    status = Column(SAEnum(Status), nullable=False, default=Status.NEW)
    source = Column(SAEnum(Source), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)

# ---------- Schemas ----------
class IncidentCreate(BaseModel):
    description: str = Field(min_length=1, max_length=2000)
    source: Source

class IncidentOut(BaseModel):
    id: int
    description: str
    status: Status
    source: Source
    created_at: datetime
    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: Status

# ---------- App ----------
app = FastAPI(title="Incidents API (mini)", version="0.1.0")

@app.post("/incidents", response_model=IncidentOut, status_code=201)
def create_incident(payload: IncidentCreate):
    \"\"\"Создать инцидент (status по умолчанию NEW).\"\\"\"
    db = SessionLocal()
    try:
        obj = IncidentORM(description=payload.description, source=payload.source, status=Status.NEW)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    finally:
        db.close()

@app.get("/incidents", response_model=List[IncidentOut])
def list_incidents(
    status: Optional[Status] = Query(None, description="Фильтр по статусу"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    \"\"\"Получить список инцидентов (с фильтром по статусу).\"\\"\"
    db = SessionLocal()
    try:
        q = db.query(IncidentORM).order_by(IncidentORM.created_at.desc(), IncidentORM.id.desc())
        if status:
            q = q.filter(IncidentORM.status == status)
        return q.offset(offset).limit(limit).all()
    finally:
        db.close()

@app.patch("/incidents/{incident_id}/status", response_model=IncidentOut)
def update_status(incident_id: int, payload: StatusUpdate):
    \"\"\"Обновить статус инцидента по id. Если не найден — 404.\"\\"\"
    db = SessionLocal()
    try:
        obj = db.query(IncidentORM).get(incident_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Incident not found")
        obj.status = payload.status
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    finally:
        db.close()
