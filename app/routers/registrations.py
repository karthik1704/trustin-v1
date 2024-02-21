from typing import Annotated
from fastapi import APIRouter, Depends, Path, status, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.dependencies.auth import get_current_user
from app.models.samples import TestType, TestingParameter
from app.models.registrations import Registration, Batch
from ..schemas.test_request_form import TRFCreate
from app.database import get_db
from ..models.test_request_forms import TRF, TestingDetail

from app.schemas.registrations import (
    RegistrationWithBatchesCreate,
    RegistrationWithBatchesUpdate,
    RegistrationWithBatchesGet,
    BatchSchema,
    BatchCreate,
    BatchUpdate
    )


router = APIRouter(prefix="/registrations", tags=["registrations"])

db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


# GET method to retrieve all registrations
@router.get("/", response_model=list[RegistrationWithBatchesGet])
def get_all_registrations(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    registrations = db.query(Registration).all()
    return registrations

# GET method to retrieve a specific registration by ID
@router.get("/{registration_id}", response_model=RegistrationWithBatchesCreate)
def get_registration(registration_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if registration is None:
        raise HTTPException(status_code=404, detail="Registration not found")
    return registration

# POST method to create a new registration
@router.post("/")
def create_registration_with_batches(registration_with_batches: RegistrationWithBatchesCreate, db: Session = Depends(get_db)) -> list[RegistrationWithBatchesGet]:
    registration_data = registration_with_batches.registration.model_dump()
    batches_data = registration_with_batches.batches

    # Create registration
    registration = Registration(**registration_data)
    db.add(registration)
    db.commit()
    db.refresh(registration)

    # Create batches associated with the registration
    for batch_data in batches_data:
        batch = Batch(**batch_data, registration_id=registration.id)
        db.add(batch)

    db.commit()

    return registration

# PUT method to update an existing registration
@router.put("/{registration_id}", response_model=RegistrationWithBatchesGet)
def update_registration_with_batches(registration_id: int, registration_with_batches: RegistrationWithBatchesUpdate, db: Session = Depends(get_db)):
    registration_data = registration_with_batches.registration.model_dump() if registration_with_batches.registration else {}
    batches_data = registration_with_batches.batches or []

    # Update registration
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if registration is None:
        raise HTTPException(status_code=404, detail="Registration not found")

    registration.update_registration(registration_data)
    registration.update_batches(db, batches_data)
    # for field, value in registration_data.items():
    #     setattr(registration, field, value)

    # Update batches associated with the registration
    # for batch_data in batches_data:
    #     batch_data= batch_data.model_dump()
    #     batch_id = batch_data.pop('id', None)
    #     if batch_id:
    #         batch = db.query(Batch).filter(Batch.id == batch_id, Batch.registration_id == registration_id).first()
    #         if batch is None:
    #             raise HTTPException(status_code=404, detail=f"Batch with id {batch_id} not found for the registration")
    #         for field, value in batch_data.items():
    #             setattr(batch, field, value)

    db.commit()
    db.refresh(registration)

    return registration

# PATCH method to partially update an existing registration
@router.patch("/{registration_id}", response_model=RegistrationWithBatchesGet)
def partial_update_registration_with_batches(registration_id: int, registration_with_batches: RegistrationWithBatchesUpdate, db: Session = Depends(get_db)):
    registration_data = registration_with_batches.registration.dict() if registration_with_batches.registration else {}
    batches_data = registration_with_batches.batches or []

    # Partially update registration
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if registration is None:
        raise HTTPException(status_code=404, detail="Registration not found")

    # for field, value in registration_data.items():
    #     setattr(registration, field, value)
    registration.patch_registration(registration_data)
    registration.patch_batches(db, batches_data)

    
    db.commit()
    db.refresh(registration)

    return registration


# GET method to retrieve all batches
@router.get("/{registration_id}/batches", response_model=list[BatchSchema])
def get_all_batches(registration_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    batches = db.query(Batch).filter(Batch.registration_id == registration_id).all()
    return batches

# GET method to retrieve a specific registration by ID
@router.get("/{registration_id}/batches/{batch_id}", response_model=BatchSchema)
def get_batch(registration_id: int, batch_id:int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    registration = db.query(Registration).filter(Batch.id == batch_id  ).first()
    if registration is None:
        raise HTTPException(status_code=404, detail="Registration not found")
    return registration

# POST method to create a new registration
@router.post("/{registration_id}/batches", response_model=BatchSchema)
def create_batch(batch: BatchCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch

# PUT method to update an existing registration
@router.put("/{registration_id}/batches/{batch_id}", response_model=BatchSchema)
def update_batch(registration_id: int,batch_id:int, updated_batch: BatchUpdate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Update fields
    for field, value in updated_batch.dict(exclude_unset=True).items():
        setattr(batch, field, value)

    db.commit()
    db.refresh(batch)
    return batch

# PATCH method to partially update an existing registration
@router.patch("/{registration_id}/batches/{batch_id}", response_model=BatchSchema)
def partial_update_batch(registration_id: int,bacth_id:int, updated_batch: BatchUpdate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == registration_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Update fields
    for field, value in updated_batch.dict(exclude_unset=True).items():
        setattr(batch, field, value)

    db.commit()
    db.refresh(batch)
    return batch