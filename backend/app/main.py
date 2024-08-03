from fastapi import FastAPI
from app.routers import hsw_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(hsw_router.router, prefix="/hsw", tags=["hsw"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Hierarchical Small World Algorithm API"}