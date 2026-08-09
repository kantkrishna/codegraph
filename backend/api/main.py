from fastapi import FastAPI

app = FastAPI(title="CodeGraph API Placeholder")

@app.get("/health")
def health_check():
    return {"status": "ok"}