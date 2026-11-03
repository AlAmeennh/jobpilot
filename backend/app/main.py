from fastapi import FastAPI

app = FastAPI(title="JobPilot API")


@app.get("/health")
def health():
    return {"status": "ok"}