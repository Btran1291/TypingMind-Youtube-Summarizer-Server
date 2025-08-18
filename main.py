from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from youtube_summarizer.routes import router as youtube_summarizer_router # Import the router

app = FastAPI(
    title="TypingMind Youtube Summarizer Plugin Server",
    description="The FastAPI server for TypingMind Youtube Summarizer plugin.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(youtube_summarizer_router, prefix="/api/v1")

@app.get("/")
async def read_root():

    return {"message": "Plugin Server is running!"}
