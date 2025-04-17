from fastapi import FastAPI
from routes import auth, pdf, summary, tables, feedback  # Import feedback route
from fastapi.staticfiles import StaticFiles
from database import engine
import models
from fastapi.middleware.cors import CORSMiddleware



# Initialize FastAPI app
app = FastAPI(title="Summaize API", description="API for PDF Summarization", version="1.0")

# Serve static files (favicon, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico")
async def get_favicon():
    return RedirectResponse(url="/static/favicon.ico")
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific domain if needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Create database tables (if not exists)
models.Base.metadata.create_all(bind=engine)

# Registering Routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(pdf.router, tags=["PDF Handling"])
app.include_router(summary.router, tags=["Summarization"])
app.include_router(tables.router, tags=["Database Tables"])
app.include_router(feedback.router, tags=["Feedback"])  # ✅ Add Feedback Router


# Root Endpoint
@app.get("/", tags=["Root"])
def home():
    return {"message": "Welcome to Summaize API!"}
