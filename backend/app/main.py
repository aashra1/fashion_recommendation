from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, users, products, interactions, recommendations
from .database import engine, Base
from .seed_data import seed_database
from .database import SessionLocal
from fastapi.staticfiles import StaticFiles



# Create tables
Base.metadata.create_all(bind=engine)

# Seed database with initial data
try:
    db = SessionLocal()
    seed_database(db)
    db.close()
except Exception as e:
    print(f"Database seeding skipped: {e}")

app = FastAPI(title="Fashion Recommendation System API", version="1.0.0")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)   # ← Make sure this is included
app.include_router(products.router)
app.include_router(interactions.router)
app.include_router(recommendations.router)

@app.get("/")
def root():
    return {
        "message": "Fashion Recommendation System API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}