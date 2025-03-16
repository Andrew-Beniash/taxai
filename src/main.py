from fastapi import FastAPI

app = FastAPI(
    title="Tax Law AI System",
    description="AI-powered tax law research and compliance system",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Tax Law AI API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
