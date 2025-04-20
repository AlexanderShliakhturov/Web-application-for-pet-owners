from fastapi import FastAPI, Depends
import os
import sys
from app.schemas import *
from app.router import router as tasks_router


# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# sys.path.append(PROJECT_ROOT)

app  = FastAPI()
app.include_router(tasks_router)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)