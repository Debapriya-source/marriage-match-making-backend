from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
import schemas
from check_email import check_email
from matches import has_similar_interests

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # validating the email address
    if user.email:
        if not check_email(user.email)["validity"]:
            raise HTTPException(
                status_code=406, detail=check_email(user.email)["msg"])
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=list[schemas.User], status_code=status.HTTP_200_OK)
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=schemas.User, status_code=status.HTTP_200_OK)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/update/{user_id}", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):

    # get the existing data
    db_user = db.query(models.User).filter(
        models.User.id == user_id).one_or_none()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # validate the email address
    if user.email:
        if not check_email(user.email)["validity"]:
            raise HTTPException(
                status_code=406, detail=check_email(user.email)["msg"])
    # Update model class variable from requested fields
    for key, value in vars(user).items():
        setattr(db_user, key, value) if value else None

    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/delete/{user_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Query the database to find the user by user_id
    db_user = db.query(models.User).filter(
        models.User.id == user_id).one_or_none()

    # If the user does not exist, return a 404 error
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    # Delete the user from the database
    db.delete(db_user)
    db.commit()

    # Return a 204 No Content response
    return {"detail": "User deleted successfully"}


@app.get("/users/matches/{user_id}", response_model=list[schemas.User])
def find_matches(user_id: int, db: Session = Depends(get_db)):
    # Get the user for whom we are finding matches
    current_user = db.query(models.User).filter(
        models.User.id == user_id).first()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find opposite gender
    opposite_gender = "male" if current_user.gender == "female" else "female"

    # Get all users of the opposite gender
    potential_matches = db.query(models.User).filter(
        models.User.gender == opposite_gender).all()

    # Filter potential matches to only include those with similar interests
    matches = [user for user in potential_matches if has_similar_interests(
        current_user, user)]

    return matches


@app.post("/users/populate/", response_model=list[schemas.User], status_code=status.HTTP_201_CREATED)
def create_bulk_users(users: schemas.BulkUserCreate, db: Session = Depends(get_db)):

    created_users = []
    for user in users.users:
        # Validate the email address
        if user.email:
            if not check_email(user.email)["validity"]:
                raise HTTPException(
                    status_code=406, detail=check_email(user.email)["msg"])

        # Check if the email already exists
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise HTTPException(
                status_code=400, detail=f"Email {user.email} already exists")

        db_user = models.User(**user.dict())
        db.add(db_user)
        created_users.append(db_user)

    db.commit()
    for created_user in created_users:
        db.refresh(created_user)

    return created_users


@app.post("/users/validate-email/")
def validate_email_endpoint(request: schemas.EmailRequest):
    result = check_email(request.email)
    if not result["validity"]:
        raise HTTPException(status_code=400, detail=result["msg"])
    return result
