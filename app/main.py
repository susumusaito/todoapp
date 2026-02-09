from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from .ai_coach import generate_coach_advice
from .database import create_db_and_tables, get_session
from .models import Todo

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, session: Session = Depends(get_session)):
    todos = session.exec(select(Todo).order_by(Todo.created_at.desc())).all()
    stats = _calc_stats(todos)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "todos": todos, "stats": stats},
    )


@app.post("/todos", response_class=HTMLResponse)
def create_todo(
    request: Request,
    title: str = Form(...),
    due_date: Optional[str] = Form(None),
    priority: str = Form("中"),
    notes: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    todo = Todo(
        title=title,
        due_date=date.fromisoformat(due_date) if due_date else None,
        priority=priority,
        notes=notes or None,
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    todos = session.exec(select(Todo).order_by(Todo.created_at.desc())).all()
    stats = _calc_stats(todos)
    return templates.TemplateResponse(
        "partials/todo_list_with_stats.html",
        {"request": request, "todos": todos, "stats": stats},
    )


@app.put("/todos/{todo_id}", response_class=HTMLResponse)
def update_todo(
    todo_id: int,
    request: Request,
    title: str = Form(...),
    status: str = Form("未着手"),
    due_date: Optional[str] = Form(None),
    priority: str = Form("中"),
    progress: int = Form(0),
    notes: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    todo = session.get(Todo, todo_id)
    if not todo:
        return HTMLResponse("Not found", status_code=404)
    todo.title = title
    todo.status = status
    todo.due_date = date.fromisoformat(due_date) if due_date else None
    todo.priority = priority
    todo.progress = progress
    todo.notes = notes or None
    todo.updated_at = datetime.now()
    session.add(todo)
    session.commit()
    session.refresh(todo)
    todos = session.exec(select(Todo).order_by(Todo.created_at.desc())).all()
    stats = _calc_stats(todos)
    return templates.TemplateResponse(
        "partials/todo_list_with_stats.html",
        {"request": request, "todos": todos, "stats": stats},
    )


@app.delete("/todos/{todo_id}", response_class=HTMLResponse)
def delete_todo(
    todo_id: int,
    request: Request,
    session: Session = Depends(get_session),
):
    todo = session.get(Todo, todo_id)
    if todo:
        session.delete(todo)
        session.commit()
    todos = session.exec(select(Todo).order_by(Todo.created_at.desc())).all()
    stats = _calc_stats(todos)
    return templates.TemplateResponse(
        "partials/todo_list_with_stats.html",
        {"request": request, "todos": todos, "stats": stats},
    )


@app.post("/ai-coach/generate", response_class=HTMLResponse)
def ai_coach_generate(
    request: Request,
    session: Session = Depends(get_session),
):
    todos = session.exec(select(Todo)).all()
    advice = generate_coach_advice(todos)
    return templates.TemplateResponse(
        "partials/ai_coach.html",
        {"request": request, "advice": advice},
    )


def _calc_stats(todos: list[Todo]) -> dict:
    total = len(todos)
    done = sum(1 for t in todos if t.status == "完了")
    in_progress = sum(1 for t in todos if t.status == "進行中")
    not_started = sum(1 for t in todos if t.status == "未着手")
    return {
        "total": total,
        "done": done,
        "in_progress": in_progress,
        "not_started": not_started,
    }
