from fastapi import FastAPI

app = FastAPI(title="Docs Chatbot")


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "chunks": 0}
