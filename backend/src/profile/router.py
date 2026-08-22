from fastapi import  Depends, HTTPException, Response, APIRouter, status # The main FastAPI class — creates the app object
from .models import Skill, Profile  # ORM model (Job) + enum (ApplicationStatus)
from ..auth.models import User
from ..database import get_db                  # Session factory — call SessionLocal() to get a DB session
from ..auth.dependencies import get_current_user
from .schemas import ProfileCreate, ProfileResponse, ProfileUpdate, SkillResponse, SkillCreate
from sqlalchemy.orm import Session


router = APIRouter(prefix="/profile", tags=["profile"])

@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(inter: ProfileCreate, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    existing = db.query(Profile).filter(Profile.user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="profile already created")

    data = inter.model_dump()
    user_profile = Profile(**data, user_id=user.id)

    db.add(user_profile)
    db.commit()
    db.refresh(user_profile)
    return user_profile

@router.get("/", response_model=ProfileResponse)
def get_profile(db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="profile not found")
    return profile

@router.put("/", response_model=ProfileResponse)
def update_profile(updated_profile: ProfileUpdate, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="profile not found")
    updates = updated_profile.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        setattr(profile, field_name, value)

    db.commit()
    db.refresh(profile)

    return profile

@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(skill: SkillCreate, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="profile not found")
    
    existing = db.query(Skill).filter(Skill.profile_id == profile.id,Skill.name.ilike(skill.name)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="skill already exists")

    new_skill = Skill(
        name     = skill.name,
        profile_id         = profile.id
    )
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

@router.get("/skills", response_model=list[SkillResponse])
def list_skills(db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="profile not found")
    return db.query(Skill).filter(Skill.profile_id == profile.id).all()

@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="profile not found")
    
    skill = db.query(Skill).filter(Skill.id == skill_id, Skill.profile_id == profile.id).first()
    if skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="skill not found")

    db.delete(skill)
    db.commit()
    return Response(status_code = 204)
