from fastapi import FastAPI, Depends
import os
import sys
from app.repository import TaskRepository
from app.schemas import *
from app.router import router as tasks_router


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

app  = FastAPI()
app.include_router(tasks_router)
    