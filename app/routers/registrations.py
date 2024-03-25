from random import sample
from typing import Annotated
import datetime
from fastapi import APIRouter, Depends, Path, status, HTTPException,Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.dependencies.auth import get_current_user
from app.models.samples import TestType, TestingParameter
from app.models.registrations import Registration, Batch, RegistrationTestParameter, Sample, SampleTestParameter
from ..schemas.test_request_form import TRFCreate
from app.database import get_db, get_async_db
from ..models.test_request_forms import TRF, TestingDetail


from app.schemas.registrations import (
    RegistrationSchema,
    RegistrationCreate,
    # RegistrationWithBatchesCreate,
    RegistrationUpdate,
    RegistrationWithBatchesGet,
    BatchSchema,
    BatchCreate,
    BatchUpdate,
    RegistrationsGet,
    RegistrationListSchema,

    SampleCreate,
    SampleSchema,
    SampleListSchema,
    PatchSample
    )


router = APIRouter(prefix="/registrations", tags=["registrations"])

db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


@router.get("/", response_model=list[RegistrationListSchema])
async def get_all_registrations(request: Request, db_session: AsyncSession = Depends(get_async_db), current_user: dict = Depends(get_current_user)):
    try:
        _registrations = await Registration.get_all(db_session,[])
        return _registrations

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET method to retrieve a specific registration by ID
@router.get("/{registration_id}", response_model=Optional[RegistrationSchema])
async def get_registration(registration_id: int, db_session: AsyncSession = Depends(get_async_db) , current_user: dict = Depends(get_current_user)):
    try:
        # _stmt = select(Registration).where(Registration.id == registration_id)
        # _result = await db_session.execute(_stmt)
        # registration = _result.scalars().first()
        _registration = await Registration.get_one(db_session,[Registration.id == registration_id])
        return _registration
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# POST method to create a new registration
@router.post("/")
async def create_registration_with_batches(registration_with_batches: RegistrationCreate, 
                                           db_session: AsyncSession = Depends(get_async_db), 
                                           current_user: dict = Depends(get_current_user)):
    time = datetime.datetime.now()
    update_dict = {
        "created_at" :time ,
        "updated_at" : time,
        "created_by" : current_user["id"],
        "updated_by" : current_user["id"],
    }
    registration_data = registration_with_batches.model_dump()
    registration_data = {**registration_data, **update_dict}
    batches_data = registration_data.pop('batches')
    test_params_data = registration_data.pop('test_params')
    code  = Registration.generate_next_code(db_session)
    registration_data.update({
        "code" : code
    })
    registration = Registration(**registration_data)
    db_session.add(registration)
    await db_session.commit()
    # Create batches associated with the registration
    for batch_data in batches_data:
        # batch_data = batch_data.model_dump()
        batch_data = {**batch_data, **update_dict}
        batch = Batch(**batch_data, registration_id=registration.id)
        db_session.add(batch)
    for params_data in test_params_data:
        # batch_data = batch_data.model_dump()
        params_data = {**params_data, **update_dict}
        print(params_data)
        test_param = RegistrationTestParameter(**params_data, registration_id=registration.id)
        db_session.add(test_param)
    

    await db_session.commit()
    await db_session.refresh(registration)
    print(registration)
    return registration

# PUT method to update an existing registration
@router.put("/{registration_id}", response_model=RegistrationSchema)
async def update_registration_with_batches(registration_id: int, registration: RegistrationUpdate, 
                                           db_session: AsyncSession = Depends(get_async_db), 
                                           current_user: dict = Depends(get_current_user)):
    registration_data = registration.model_dump()
    batches_data = registration_data.pop("batches",[])
    test_params_data = registration_data.pop("test_params",[])
    print("reg with batches update")
    registration = await Registration.get_one(db_session,[Registration.id == registration_id])
    if registration is None:
        raise HTTPException(status_code=404, detail="Registration not found")
    time = datetime.datetime.now()
    update_dict = {
                        "updated_at" : time,
                        "updated_by" : current_user["id"],
                    }
    registration_data = {**registration_data, **update_dict}
    registration.update_registration(registration_data)
    if batches_data:
        await registration.update_batches(db_session, batches_data, current_user)
    if test_params_data:
        await registration.update_test_prams(db_session, test_params_data, current_user)

    await db_session.commit()
    await db_session.refresh(registration)

    return registration

# # PATCH method to partially update an existing registration
# @router.patch("/{registration_id}", response_model=RegistrationWithBatchesGet)
# def partial_update_registration_with_batches(registration_id: int, registration_with_batches: RegistrationUpdate, db: Session = Depends(get_db)):
#     registration_data = registration_with_batches.registration.dict() if registration_with_batches.registration else {}
#     batches_data = registration_with_batches.batches or []

#     # Partially update registration
#     registration = db.query(Registration).filter(Registration.id == registration_id).first()
#     if registration is None:
#         raise HTTPException(status_code=404, detail="Registration not found")

#     # for field, value in registration_data.items():
#     #     setattr(registration, field, value)
#     registration.patch_registration(registration_data)
#     registration.patch_batches(db, batches_data)

    
#     db.commit()
#     db.refresh(registration)

#     return registration


# GET method to retrieve all batches
@router.get("/{registration_id}/batches", response_model=list[BatchSchema])
async def get_all_batches(registration_id: int, db_session: AsyncSession = Depends(get_async_db), current_user: dict = Depends(get_current_user)):
    batches = await Batch.get_all(db_session,[Batch.registration_id == registration_id])
    return batches

# GET method to retrieve a specific registration by ID
@router.get("/{registration_id}/batches/{batch_id}", response_model=BatchSchema)
async def get_batch(registration_id: int, batch_id:int, db_session: AsyncSession = Depends(get_async_db), current_user: str = Depends(get_current_user)):
    batch = await Batch.get_one(db_session,[Batch.registration_id == registration_id])
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

# POST method to create a new registration
@router.post("/{registration_id}/batches", response_model=BatchSchema)
async def create_batch(batch: BatchCreate,  db_session: AsyncSession = Depends(get_async_db), current_user: dict = Depends(get_current_user)):
    
    time = datetime.datetime.now()
    update_dict = {
        "created_at" :time ,
        "updated_at" : time,
        "created_by" : current_user["id"],
        "updated_by" : current_user["id"],
    }
    batch_data = batch.model_dump()
    batch_data = {**batch_data, **update_dict}
    batch = Batch(**batch_data)
    db_session.add(batch)
    await db_session.commit()
    await db_session.refresh(batch)
    return batch

# PUT method to update an existing registration
@router.put("/{registration_id}/batches/{batch_id}", response_model=BatchSchema)
async def update_batch(registration_id: int,batch_id:int, updated_batch: BatchUpdate, db_session: AsyncSession = Depends(get_async_db), current_user: dict = Depends(get_current_user)):
    
    batch_data = updated_batch.model_dump()
    
    batch = await Batch.get_one(db_session,[Batch.id == batch_id])
    if batch is None:
        raise HTTPException(status_code=404, detail="Registration not found")
    time = datetime.datetime.now()
    update_dict = {
                        "updated_at" : time,
                        "updated_by" : current_user["id"],
                    }
    batch_data = {**batch_data, **update_dict}
    batch.update_batch(batch_data)
   
    await db_session.commit()
    await db_session.refresh(batch)

    return batch





# GET method to retrieve all samples
@router.get("/{registration_id}/samples", response_model=list[SampleListSchema])
async def get_registration_samples(registration_id: int, db_session: AsyncSession = Depends(get_async_db), current_user: dict = Depends(get_current_user)):
    print("coming inside-reg")
    samples = await Sample.get_all(db_session,[Sample.registration_id == registration_id])
    return samples

# GET method to retrieve a specific registration by ID
@router.get("/{registration_id}/samples/{sample_id}", response_model=SampleSchema)
async def get_registration_sample(registration_id: int, sample_id:int, db_session: AsyncSession = Depends(get_async_db), current_user: str = Depends(get_current_user)):
    sample = await Sample.get_one(db_session,[Sample.id == sample_id])
    if sample is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return sample

# POST method to create a new registration
@router.post("/{registration_id}/samples", response_model=list[SampleListSchema])
async def create_sample_with_testparams(registration_id : int, sample_with_testparams_list: list[SampleCreate], 
                                           db_session: AsyncSession = Depends(get_async_db), 
                                           current_user: dict = Depends(get_current_user)) -> list[SampleListSchema]:
    time = datetime.datetime.now()
    update_dict = {
        "status_id" : 1,
        "assigned_to" : current_user["id"],
        "created_at" :time ,
        "updated_at" : time,
        "created_by" : current_user["id"],
        "updated_by" : current_user["id"], 
    }
    print("samplae creattion")
    result = []
    for sample_with_testparams in sample_with_testparams_list:
        sample_data = sample_with_testparams.model_dump()
        sample_data = {**sample_data, **update_dict}
        test_params_data = sample_data.pop('test_params')
        # test_params_data = sample_data.pop('test_params')
        print(sample_data)
        sample_id = Sample.generate_next_code(db_session)
        sample_data.update({
            "sample_id" : sample_id
        })
        sample = Sample(**sample_data, registration_id = registration_id)
        db_session.add(sample)
        await db_session.commit()
        # Create batches associated with the registration
        # for batch_data in batches_data:
        #     # batch_data = batch_data.model_dump()
        #     batch_data = {**batch_data, **update_dict}
        #     batch = Batch(**batch_data, registration_id=registration.id)
        #     db_session.add(batch)
        update_dict = {
            "created_at" :time ,
            "updated_at" : time,
            "created_by" : current_user["id"],
            "updated_by" : current_user["id"], 
            }
        for params_data in test_params_data:
            # batch_data = batch_data.model_dump()
            # params_data["test_parameter_id"] = 2
            params_data = {**params_data, **update_dict}
            print(params_data)
            test_param = SampleTestParameter(**params_data, sample_id=sample.id)
            db_session.add(test_param)
        

        await db_session.commit()
        await db_session.refresh(sample)
        result.append(sample)
        # result.append({
        #     "id": sample.id,
        #     "sample_id": sample.sample_id,
        #     "name": sample.name,
        #     "registration_id" : sample.registration_id,
        #     "status_id" : sample.status_id,
        #     "department" : sample.department,
        #     "assigned_to" : sample.assigned_to,
        #     "batch_id": sample.batch_id,
        #     "status": sample.registration_id,
        #     "created_at": sample.created_at,
        #     "updated_at": sample.updated_at,
        #     "created_by": sample.created_by,
        #     "updated_by": sample.updated_by
    
        # })
    print(result)
    return result

# # GET method to retrieve all samples
# @router.get("/samples1", response_model=list[SampleListSchema])
# async def get_all_samples(db_session: AsyncSession = Depends(get_async_db), current_user: dict = Depends(get_current_user)):
#     print("coming inside")
#     samples = await Sample.get_all(db_session,[])
#     return samples

# # GET method to retrieve a specific sample by ID
# @router.get("/samples/{sample_id}", response_model=SampleSchema)
# async def get_sample(sample_id:int, db_session: AsyncSession = Depends(get_async_db), current_user: str = Depends(get_current_user)):
#     sample = await Sample.get_one(db_session,[Sample.id == sample_id])
#     if sample is None:
#         raise HTTPException(status_code=404, detail="Sample not found")
#     return sample

# # PUT method to update an existing registration
# @router.patch("/samples/{sample_id}", response_model=SampleSchema)
# async def patch_sample(sample_id:int, updated_sample: PatchSample, db_session: AsyncSession = Depends(get_async_db), current_user: dict = Depends(get_current_user)):
    
#     sample_data = updated_sample.model_dump()
    
#     sample = await Sample.get_one(db_session,[Batch.id == sample_id])
#     if sample is None:
#         raise HTTPException(status_code=404, detail="Sample not found")
#     time = datetime.datetime.now()
#     update_dict = {
#                         "updated_at" : time,
#                         "updated_by" : current_user["id"],
#                     }
#     # if "comment" in sample_data:
#     comment = sample_data.pop("comment","")
#     sample_data = {**sample_data, **update_dict}
#     await sample.update_sample(sample_data)
#     if sample_data.get("status","") == "Submitted":
#         await sample.create_workflow(db_session, current_user)
#     await sample.create_history(db_session, current_user)
#     await db_session.commit()
#     await db_session.refresh(sample)

#     return sample


