from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.api import auth
from app.api import resource
from app.api import booking

app = FastAPI(title="Library & Resource Booking System")

app.include_router(auth.router)
app.include_router(resource.router)
app.include_router(booking.router)

@app.get("/")
def root():
    return {"message": "Resource Booking System API is running"}

@app.get("/db_check")
def db_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    return {
        "db_connected": result.scalar() == 1
    }