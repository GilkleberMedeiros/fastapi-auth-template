from fastapi import FastAPI

from app.env import PORT, DEBUG
from app.db import init_db
from app.routes import auth


app = FastAPI(
    title="FastAPI JWT Auth Practice", 
    debug=DEBUG, 
)

# init db
init_db()

# Include routes
app.include_router(auth.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1" if DEBUG else "0.0.0.0", port=PORT, reload=DEBUG) 