from fastapi import FastAPI, Depends, HTTPException, Response, status # The main FastAPI class — creates the app object
from models import ApplicationStatus, Internship, User   # ORM model (Internship) + enum (ApplicationStatus)
from database import get_db                  # Session factory — call SessionLocal() to get a DB session
from dependencies import get_current_user
from schemas import InternshipCreate, InternshipResponse, InternshipUpdate,  UserCreate, UserResponse, UserLogin     
from sqlalchemy.orm import Session
from security import hash_password, verify_password 
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from jose import jwt
import logging

load_dotenv()

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/health")
def health_check():
    return {"status": "ok"}

#Depends: means run this function inside fisrt , and use whetever it return 
@app.post("/internships")
def create_internships(inter: InternshipCreate, db: Session=Depends(get_db), user: User=Depends(get_current_user)): 
    new_internship = Internship(
        company_name     = inter.company_name,
        position         = inter.position,
        location         = inter.location,
        application_date = inter.application_date,
        deadline         = inter.deadline,
        job_link         = inter.job_link,
        notes            = inter.notes,
        status           = ApplicationStatus.SAVED,
        user_id          = user.id
    )

    db.add(new_internship)
    db.commit()
    db.refresh(new_internship)
    return new_internship


@app.get("/internships", response_model=list[InternshipResponse])
def get_all_internship(db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    internships = db.query(Internship).filter(Internship.user_id == user.id).all()
    return internships


@app.get("/internships/{internship_id}", response_model=InternshipResponse)
def get_id_internship(internship_id: int, db: Session = Depends(get_db), user: User=Depends(get_current_user)):
    internship = db.query(Internship).filter(Internship.id == internship_id, Internship.user_id == user.id).first()
    if internship is None:
        raise HTTPException(status_code = 404, detail = "Internship not found")
    return internship


@app.put("/internships/{internship_id}", response_model=InternshipResponse)
def update_internship(internship_id: int, updated_data: InternshipUpdate, db: Session = Depends(get_db), user: User=Depends(get_current_user)):
    internship = db.query(Internship).filter(Internship.id == internship_id, Internship.user_id == user.id).first()
    if internship is None:
        raise HTTPException(status_code = 404, detail = "Internship not found")
    updates = updated_data.model_dump(exclude_unset=True)
    # model_dump() is the converstion step that turns it into a plain dict specificlly so it can be loopes over
    for field_name, value in updates.items():
        setattr(internship, field_name, value)
    
    db.commit()
    db.refresh(internship)

    return internship

@app.delete("/internships/{internship_id}")
def delete_internship(internship_id: int, db: Session = Depends(get_db), user: User=Depends(get_current_user)):
    internship = db.query(Internship).filter(Internship.id == internship_id, Internship.user_id == user.id).first()
    if internship is None:
        raise HTTPException(status_code = 404, detail = "Internship not found")
    db.delete(internship)
    db.commit()

    return Response(status_code = 204)


@app.post("/register", response_model=UserResponse)
def create_user(user: UserCreate, db: Session=Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first() 
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="account already exist")
    new_user = User(
        email = user.email,
        hashed_password = hash_password(user.password)   
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login")
def login_user(user: UserLogin, db: Session=Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing is None:
        logger.warning(f"user not found for the email {user.email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    
    is_password_correct = verify_password(user.password, existing.hashed_password)
    if is_password_correct is False:
        logger.warning(f"wrong password for user id: [{existing.id}]")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    logger.info(f"user id[{existing.id}] logged in")
    payload = { 
        "sub": str(existing.id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    }

    token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return {"access_token": token, "token_type": "bearer"}
