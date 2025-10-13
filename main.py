from fastapi import FastAPI


app = FastAPI(
    title="My FastAPI App",
    description="A simple FastAPI starter template",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI base project!"}