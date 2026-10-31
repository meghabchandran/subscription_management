from fastapi import FastAPI

from database import Base, engine
from models.user import User
from models.customer import Customer
from routes import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Brightloop Subscription Management API"
)

app.include_router(auth.router)


@app.get("/")
def read_root():
    return {
        "message": "Brightloop Backend is running!"
    }