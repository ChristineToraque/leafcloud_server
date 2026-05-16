import os
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, auth, database
from .database import engine, get_db
from .discovery import discovery_service
from dotenv import load_dotenv

load_dotenv()

# Create tables (Commented out because we use Alembic for migrations)
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LeafCloud Server V2 API")

@app.on_event("startup")
async def start_up_tasks():
    # Seed admin user
    seed_admin_user()
    
    # Start Zeroconf discovery
    port = int(os.getenv("PORT", 8000))
    await discovery_service.start(port=port)

@app.on_event("shutdown")
async def shutdown_tasks():
    # Stop Zeroconf discovery
    await discovery_service.stop()

def seed_admin_user():
    db = database.SessionLocal()
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@leafcloud.com")
        admin_user = db.query(models.User).filter(models.User.email == admin_email).first()
        
        if not admin_user:
            print(f"Seeding admin user: {admin_email}")
            hashed_password = auth.get_password_hash(os.getenv("ADMIN_PASSWORD", "admin123"))
            new_admin = models.User(
                email=admin_email,
                name=os.getenv("ADMIN_NAME", "Super Admin"),
                hashed_password=hashed_password
            )
            db.add(new_admin)
            db.commit()
            print("Admin user seeded successfully.")
    except Exception as e:
        print(f"Error seeding admin user: {e}")
    finally:
        db.close()

@app.post("/auth/login", response_model=schemas.LoginResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == request.email).first()

    if not user or not auth.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )

    return {
        "status": "success",
        "token": access_token,
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }

@app.get("/")
def read_root():
    return {"message": "Welcome to LeafCloud Server V2 API"}
