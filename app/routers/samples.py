from random import sample
from typing import Annotated
import datetime
from fastapi import APIRouter, Depends, Path, status, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.dependencies.auth import get_current_user
from app.models.samples import TestType, TestingParameter
from app.models.registrations import (
    Registration,
    Batch,
    RegistrationTestParameter,
    Sample,
    SampleTestParameter,
    SampleWorkflow,
    SampleStatus,
)
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
    SampleListWithPaginationSchema,
    SampleSchema,
    SampleListSchema,
    PatchSample,
    SampleTestParameterSchema,
    SampleUpdate,
)

router = APIRouter(prefix="/samples", tags=["samples"])

db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]


# GET method to retrieve all samples
@router.get("/", response_model=Optional[SampleListWithPaginationSchema])
async def get_all_samples_with_pagination(
    db_session: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user),
    page: int = 1,
    size: int = 10,
    search: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "desc",
):
    print("coming inside")
    print(current_user)
    samples = []
    if current_user.get("dept_id", "") in (1, 2, 5, 6):
        samples = await Sample.get_all_with_pagination(
            db_session, [], page, size, search, sort_by, sort_order
        )
    elif current_user.get("role_id", "") == 3:
        samples = await Sample.get_for_qa_hod_with_pagination(
            db_session, current_user, [], page, size, search, sort_by, sort_order
        )
    elif current_user.get("role_id", "") == 4:
        samples = await Sample.get_for_qa_analyst_with_pagination(
            db_session, current_user, [], page, size, search, sort_by, sort_order
        )

    return samples


@router.get("/all", response_model=Optional[list[SampleListSchema]])
async def get_all_samples(
    db_session: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user),
):
    print("coming inside")
    print(current_user)
    samples = []
    if current_user.get("dept_id", "") in (1, 2, 5, 6):
        samples = await Sample.get_all(db_session, [])
    elif current_user.get("role_id", "") == 3:
        samples = await Sample.get_for_qa_hod(db_session, current_user, [])
    elif current_user.get("role_id", "") == 4:
        samples = await Sample.get_for_qa_analyst(db_session, current_user, [])

    return samples


@router.get("/without-reg", response_model=Optional[list[SampleListSchema]])
async def get_all_sample_without_reg(
    db_session: AsyncSession = Depends(get_async_db),
    current_user: str = Depends(get_current_user),
):
    sample = await Sample.get_all(db_session, [Sample.registration_id == None])
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


# GET method to retrieve a specific sample by ID
@router.get("/{sample_id}", response_model=SampleSchema)
async def get_sample(
    sample_id: int,
    db_session: AsyncSession = Depends(get_async_db),
    current_user: str = Depends(get_current_user),
):
    sample = await Sample.get_one(db_session, [Sample.id == sample_id])
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.post("/", response_model=list[SampleListSchema])
async def create_sample_with_testparams(
    sample_with_testparams_list: list[SampleCreate],
    db_session: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user),
) -> list[SampleListSchema]:
    time = datetime.datetime.now()
    update_dict = {
        "status_id": 1,
        "assigned_to": current_user["id"],
        "created_at": time,
        "updated_at": time,
        "created_by": current_user["id"],
        "updated_by": current_user["id"],
    }
    print("samplae creattion")
    result = []
    for sample_with_testparams in sample_with_testparams_list:
        sample_data = sample_with_testparams.model_dump()
        sample_data = {**sample_data, **update_dict}
        test_params_data = sample_data.pop("test_params")
        # test_params_data = sample_data.pop('test_params')
        print(sample_data)
        sample_id = await Sample.generate_next_code(
            db_session, sample_data.get("registration_id")
        )
        sample_data.update({"sample_id": sample_id})
        sample = Sample(**sample_data)
        db_session.add(sample)
        await db_session.commit()
        # Create batches associated with the registration
        # for batch_data in batches_data:
        #     # batch_data = batch_data.model_dump()
        #     batch_data = {**batch_data, **update_dict}
        #     batch = Batch(**batch_data, registration_id=registration.id)
        #     db_session.add(batch)
        test_update_dict = {
            "created_at": time,
            "updated_at": time,
            "created_by": current_user["id"],
            "updated_by": current_user["id"],
        }
        for params_data in test_params_data:
            # batch_data = batch_data.model_dump()
            # params_data["test_parameter_id"] = 2
            params_data = {**params_data, **test_update_dict}
            print(params_data)
            test_param = SampleTestParameter(**params_data, sample_id=sample.id)
            db_session.add(test_param)

        await db_session.commit()
        await db_session.refresh(sample)
        result.append(sample)

    print(result)
    return result


@router.put("/{sample_id}", response_model=SampleSchema)
async def update_sample(
    sample_id: int,
    sample_update: SampleUpdate,
    db_session: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user),
):
    sample_data = sample_update.model_dump()
    test_params_data = sample_data.pop("test_params", [])

    sample = await Sample.get_one(db_session, [Sample.id == sample_id])
    if sample is None:
        raise HTTPException(status_code=404, detail="Registration not found")
    time = datetime.datetime.now()
    update_dict = {
        "updated_at": time,
        "updated_by": current_user["id"],
    }
    sample_data = {**sample_data, **update_dict}
    await sample.update_sample(sample_data)

    if test_params_data:
        await sample.update_test_params(db_session, test_params_data, current_user)

    await db_session.commit()
    await db_session.refresh(sample)

    return sample


# PUT method to update an existing registration
@router.patch("/{sample_id}",status_code=status.HTTP_204_NO_CONTENT)
async def patch_sample(
    sample_id: int,
    updated_sample: PatchSample,
    db_session: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user),
):

    sample_data = updated_sample.model_dump(exclude_unset=True)

    sample = await Sample.get_one(db_session, [Sample.id == sample_id])
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    time = datetime.datetime.now()
    update_dict = {
        "updated_at": time,
        "updated_by": current_user["id"],
    }
    # if "comment" in sample_data:
    comments = sample_data.pop("comments", "")
    test_type_id = sample_data.pop("test_type_id", None)
    test_params = sample_data.pop("test_params", [])
    sample_data = {**sample_data, **update_dict}
    for test_param_data in test_params:
        # test_param_data = test_param_data.model_dump()
        print(test_param_data)
        test_param_data = {**test_param_data, **update_dict}
        test_param_id = test_param_data.get("id")
        test_param = await SampleTestParameter.get_one(
            db_session, [SampleTestParameter.id == test_param_id]
        )
        print(test_param)
        if test_param:
            await test_param.update_sample_test_param(test_param_data)
    prev_status = sample.status
    if "status_id" in sample_data:
        status_id = sample_data.pop("status_id","")

    await sample.update_sample(sample_data)
    sample_data.update({
        "status_id" : status_id
    })
    if sample_data.get("status", "") == "Submitted" and prev_status != "Submitted":
        await sample.create_workflow(db_session, current_user)
        history = {
            "sample_id": sample_id,
            "created_at": time,
            "created_by": current_user["id"],
            "from_status_id": 1,
            "to_status_id": 2,
        }
        if sample_data.get("assigned_to", ""):
            print("assinged_to")
            print(sample_data.get("assigned_to", ""))
            history.update({"assigned_to": sample_data.get("assigned_to", "")})
        if comments:
            history.update({"comments": comments})

        await sample.create_history(db_session, current_user, history)
    else:
        if sample_data.get("status_id", "") and test_type_id:

            progress = await SampleWorkflow.get_one(
                db_session,
                [
                    SampleWorkflow.sample_id == sample_id,
                    SampleWorkflow.test_type_id == test_type_id,
                    SampleWorkflow.status == "In Progress",
                ],
            )

            progres_status_id = progress.sample_status_id if progress else 0
            print("progres_status_id", progres_status_id)
            if progress and sample_data.get("status_id", "") == progres_status_id + 1:
                # moving forward
                update_dict = {
                    "status": "Done",
                    "updated_at": time,
                    "updated_by": current_user["id"],
                }
                if sample_data.get("assigned_to", ""):
                    update_dict.update(
                        {"assigned_to": sample_data.get("assigned_to", "")}
                    )

                await progress.update_workflow(update_dict)

                new_status = await SampleWorkflow.get_one(
                    db_session,
                    [
                        SampleWorkflow.sample_id == sample_id,
                        SampleWorkflow.sample_status_id == progres_status_id + 1,
                        SampleWorkflow.test_type_id == test_type_id
                    ],
                )
                if new_status:
                    update_dict = {
                        "status": "In Progress",
                        "updated_at": time,
                        "updated_by": current_user["id"],
                    }
                    if sample_data.get("assigned_to", ""):
                        update_dict.update(
                            {"assigned_to": sample_data.get("assigned_to", "")}
                        )

                    await new_status.update_workflow(update_dict)
                # history = {
                # "sample_id" : sample_id,
                # "created_at" : time,
                # "created_by": current_user["id"],
                # "to_status_id" : sample_data.get("status_id",""),
                # "from_status_id" : progres_status_id,
                # "comments" : sample_data.get("comments","")
                # }
                # if sample_data.get("assigned_to",""):
                #     history.update({
                #         "assigned_to" : sample_data.get("assigned_to","")
                #     })
                # if comments:
                #     history.update({
                #         "comments" : comments
                #     })

                # await sample.create_history(db_session, current_user,history)
            elif progress and sample_data.get("status_id", "") == progres_status_id - 1:
                print('how')
                # moving forward
                update_dict = {
                    "status": "Yet To Start",
                    "updated_at": time,
                    "updated_by": current_user["id"],
                }
                if sample_data.get("assigned_to", ""):
                    update_dict.update(
                        {"assigned_to": sample_data.get("assigned_to", "")}
                    )
                await progress.update_workflow(update_dict)

                new_status = await SampleWorkflow.get_one(
                    db_session,
                    [
                        SampleWorkflow.sample_id == sample_id,
                        SampleWorkflow.sample_status_id == progres_status_id - 1,
                        SampleWorkflow.test_type_id == test_type_id
                    ],
                )
                if new_status:
                    update_dict = {
                        "status": "In Progress",
                        "updated_at": time,
                        "updated_by": current_user["id"],
                    }
                    if sample_data.get("assigned_to", ""):
                        update_dict.update(
                            {"assigned_to": sample_data.get("assigned_to", "")}
                        )
                    await new_status.update_workflow(update_dict)
            if progress:
                history = {
                    "sample_id": sample_id,
                    "test_type_id" : test_type_id,
                    "created_at": time,
                    "created_by": current_user["id"],
                    "to_status_id": sample_data.get("status_id", ""),
                    "from_status_id": progres_status_id,
                    "comments": sample_data.get("comments", ""),
                }
                if sample_data.get("assigned_to", ""):
                    history.update({"assigned_to": sample_data.get("assigned_to", "")})
                if comments:
                    history.update({"comments": comments})

                await sample.create_history(db_session, current_user, history)
            await db_session.commit()
            #auto update sample status
            mech = await SampleWorkflow.get_one(
                db_session,
                [
                    SampleWorkflow.sample_id == sample_id,
                    SampleWorkflow.test_type_id == 1,
                    SampleWorkflow.status == "In Progress",
                ],
            )
            micro = await SampleWorkflow.get_one(
                db_session,
                [
                    SampleWorkflow.sample_id == sample_id,
                    SampleWorkflow.test_type_id == 2,
                    SampleWorkflow.status == "In Progress",
                ],
            )
            if mech and micro and mech.sample_status_id == micro.sample_status_id:
                update_data = {
                    "status_id" : mech.sample_status_id
                }
                await sample.update_sample(update_data)
    await db_session.commit()
    await db_session.refresh(sample)

    # return sample
