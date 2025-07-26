from fastapi import FastAPI

app = FastAPI(
    title="SweetShop API",
    description="A TDD-developed sweet shop management system",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to SweetShop API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
