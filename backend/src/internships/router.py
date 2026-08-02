from fastapi import  Depends, HTTPException, Response, APIRouter # The main FastAPI class — creates the app object
from .models import ApplicationStatus, Internship  # ORM model (Internship) + enum (ApplicationStatus)
from ..auth.models import User
from ..database import get_db                  # Session factory — call SessionLocal() to get a DB session
from ..auth.dependencies import get_current_user
from .schemas import InternshipCreate, InternshipResponse, InternshipUpdate     
from sqlalchemy.orm import Session


router = APIRouter(prefix="/internships", tags=["internships"])

@router.post("/", status_code=201)
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


@router.get("/", response_model=list[InternshipResponse])
def get_all_internship(db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    internships = db.query(Internship).filter(Internship.user_id == user.id).all()
    return internships


@router.get("/{internship_id}", response_model=InternshipResponse)
def get_id_internship(internship_id: int, db: Session = Depends(get_db), user: User=Depends(get_current_user)):
    internship = db.query(Internship).filter(Internship.id == internship_id, Internship.user_id == user.id).first()
    if internship is None:
        raise HTTPException(status_code = 404, detail = "Internship not found")
    return internship


@router.put("/{internship_id}", response_model=InternshipResponse)
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

@router.delete("/{internship_id}")
def delete_internship(internship_id: int, db: Session = Depends(get_db), user: User=Depends(get_current_user)):
    internship = db.query(Internship).filter(Internship.id == internship_id, Internship.user_id == user.id).first()
    if internship is None:
        raise HTTPException(status_code = 404, detail = "Internship not found")
    db.delete(internship)
    db.commit()

    return Response(status_code = 204)
