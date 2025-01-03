from fastapi import FastAPI

from src.routers import router

app = FastAPI(
    title="Event Data API",
    description="API for managing and retrieving event data",
    version="1.0.0",
    docs_url="/docs",  # URL for the Swagger UI documentation
    redoc_url="/redoc",  # URL for ReDoc documentation
)

# Connect the router to the FastAPI app
app.include_router(
    router=router
)

# Define a root route for health check or basic information
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint for basic health check or welcome message.
    """
    return {"message": "Welcome to the ForestBook API"}

# Run the app using Uvicorn if the script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8005, reload=False)
