from fastapi import FastAPI

app = FastAPI(
    title="Brightloop Subscription Management API"
)


@app.get("/")
def read_root():
    return {
        "message": "Brightloop Backend is running!"
    }