from fastapi import FastAPI, Depends, HTTPException, Response # The main FastAPI class — creates the app object
from models import ApplicationStatus, Internship   # ORM model (Internship) + enum (ApplicationStatus)
from database import SessionLocal                  # Session factory — call SessionLocal() to get a DB session
from schemas import InternshipCreate, InternshipResponse, InternshipUpdate      
from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    db = SessionLocal() #open a session
    try:
        yield db #hand it to whoever ask it 
    finally:
        db.close() #always close it when done, even if it crashes

@app.get("/health")
def health_check():
    return {"status": "ok"}

#Depends: means run this function inside fisrt , and use whetever it return 
@app.post("/internships")
def create_internships(inter: InternshipCreate, db: Session=Depends(get_db)): 
    new_internship = Internship(
        company_name     = inter.company_name,
        position         = inter.position,
        location         = inter.location,
        application_date = inter.application_date,
        deadline         = inter.deadline,
        job_link         = inter.job_link,
        notes            = inter.notes,
        status           = ApplicationStatus.SAVED    # Always start as SAVED
    )

    db.add(new_internship)
    db.commit()
    db.refresh(new_internship)
    return new_internship

@app.get("/internships", response_model=list[InternshipResponse])
def get_all_internship(db: Session=Depends(get_db)):
    internships = db.query(Internship).all()
    return internships

#response_model is the instruction that tells FastAPI: "here's the Pydantic schema to use for that conversion on the way OUT." It does two jobs:

#Filtering/shaping — it decides exactly which fields appear in the JSON response, in what shape. 
# If your SQLAlchemy object had extra internal fields you didn't want exposed, 
# response_model would strip them out — only fields declared in the schema get included.
#Validation on the way out — it double-checks the data you're returning actually matches the schema's types before sending it as JSON.


@app.get("/internships/{internship_id}", response_model=InternshipResponse)
def get_id_internship(internship_id: int, db: Session = Depends(get_db)):
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if internship is None:
        raise HTTPException(status_code = 404, detail = "Internship not found")
    return internship


@app.put("/internships/{internship_id}", response_model=InternshipResponse)
def update_internship(internship_id: int, updated_data: InternshipUpdate, db: Session = Depends(get_db)):
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
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
def delete_internship(internship_id: int, db: Session = Depends(get_db)):
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if internship is None:
        raise HTTPException(status_code = 404, detail = "Internship not found")
    db.delete(internship)
    db.commit()

    return Response(status_code = 204)

