from fastapi import FastAPI
from .routers import auth

app = FastAPI(
    title="SweetShop API",
    description="A TDD-developed sweet shop management system",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Welcome to SweetShop API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
