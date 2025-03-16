from fastapi import FastAPI
import uvicorn

# Create FastAPI instance
app = FastAPI(
    title="AI-Powered Tax Law Application",
    description="A system for tax law research, document processing, and compliance validation",
    version="0.1.0",
)

@app.get("/")
async def root():
    """Root endpoint to verify API is running"""
    return {
        "status": "success",
        "message": "AI-Powered Tax Law Application API is running",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
