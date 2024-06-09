from random import sample
from typing import Annotated, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Path, status, HTTPException,Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func,join, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.dependencies.auth import get_current_user
from app.models.customers import Customer, CustomerFollowUp
from app.models.samples import TestType, TestingParameter, Product
from app.models.users import User
from app.models.registrations import Registration, Batch, RegistrationTestParameter, \
    Sample, SampleTestParameter,SampleWorkflow,SampleStatus
from ..schemas.test_request_form import TRFCreate
from app.database import get_db, get_async_db
from ..models.test_request_forms import TRF, TestingDetail


# from app.schemas.registrations import (
#     RegistrationSchema,
#     RegistrationCreate,
#     # RegistrationWithBatchesCreate,
#     RegistrationUpdate,
#     RegistrationWithBatchesGet,
#     BatchSchema,
#     BatchCreate,
#     BatchUpdate,
#     RegistrationsGet,
#     RegistrationListSchema,

#     SampleCreate,
#     SampleSchema,
#     SampleListSchema,
#     PatchSample,
#     SampleTestParameterSchema
#     )

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

db_dep = Annotated[Session, Depends(get_db)]
user_dep = Annotated[dict, Depends(get_current_user)]



# GET method to retrieve all samples
@router.get("/")
async def get_dashboard_data(db_session: AsyncSession = Depends(get_async_db), current_user: dict = Depends(get_current_user), 
                            start_date_str : str = "", end_date_str : str = "")->dict:
    print("coming inside")
    print(current_user)
    customer_count = await db_session.scalar(select(func.count()).select_from(Customer))
    product_count = await db_session.scalar(select(func.count()).select_from(Product))
    # trf_count = await db_session.scalar(select(func.count()).select_from(TRF))
    registration_count = select(func.count()).select_from(Registration)
    print(start_date_str)
    print(start_date_str)
    start_date : datetime | None = None
    end_date : datetime | None = None
    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%d-%m-%Y")
        registration_count = registration_count.where(Registration.created_at >= start_date)
    if end_date_str:
        end_date = datetime.strptime(end_date_str, "%d-%m-%Y")
        registration_count = registration_count.where(Registration.created_at <= end_date) 
    registration_count = await db_session.scalar(registration_count)    
    # followup_count = await db_session.scalar(select(func.count()).select_from(CustomerFollowUp).where(CustomerFollowUp.marketing_status.notin_(["WON", "LOST"])))

    
    result : Dict[str, Any] = {
        "customer" : customer_count,
        "product" : product_count,
        "registration_count" : registration_count,        
        # "followup_count" : followup_count
    }
    if current_user.get("dept_id", "") == 3:
        # user = await db_session.scalar(select(User).select_from(User).where(User.id == current_user.get("id")))
        user = await db_session.scalar(
            select(User)
            .select_from(User)
            .where(User.id == current_user.get("id"))
            
        )

        if user:
            sample_count =  (select(func.count())
                .select_from(Sample)
                .where(Sample.test_type_id == user.qa_type_id))
            if start_date:
                sample_count = sample_count.where(Sample.created_at >= start_date)
            if end_date:
                sample_count = sample_count.where(Sample.created_at <= end_date) 
            sample_count = await db_session.scalar(sample_count)
        else:
            # Handle the case where the user is not found
            sample_count = 0  # Or any other appropriate value
        result.update({
            "sample_count" : sample_count
        })
    elif current_user.get("dept_id", "") in (1,2,5,6):
        sample_count = (select(func.count())
                        .select_from(Sample))
                
        if start_date:
                sample_count = sample_count.where(Sample.created_at >= start_date)
        if end_date:
            sample_count = sample_count.where(Sample.created_at <= end_date) 
        sample_count = await db_session.scalar(sample_count)
        # Calculate the start and end dates for the query
        # current_date = datetime.now().date()
        # start_date = current_date - timedelta(days=current_date.weekday())
        # end_date = start_date + timedelta(days=7)

        

        # Query to get the count of registrations grouped by week
        weekly_registration_counts = (
           
                 select(
                   cast(func.DATE_TRUNC('week', Registration.created_at), Date).label('week_start'),
                    func.count().label('registration_count')
                )
        
            )
        
        if start_date:
            weekly_registration_counts = weekly_registration_counts.where(Registration.created_at >= start_date)
        if end_date:
            weekly_registration_counts = weekly_registration_counts.where(Registration.created_at <= end_date) 
        
        weekly_registration_counts = await db_session.execute(
                weekly_registration_counts
                .group_by('week_start')
                .order_by('week_start')
            )
            
        
        
        results = []
        for row in weekly_registration_counts.all():
            
            # SQLAlchemy row object for User

            result_dict = {
                # "assign_to": customer_followup.assign_to,
                "week": row[0],  # Assuming followup_count is an attribute of CustomerFollowUp
                # Add other fields from CustomerFollowUp and User as needed
                "count": row[1]
                
            }
            results.append(result_dict)
        
        result.update(
            {
                "sample_count": sample_count,
                "registration_data": results
            }
        )
    # if current_user.get("dept_id") in (1,2,4,5,6):
    #     join_condition = CustomerFollowUp.assign_to == User.id

    #     # Execute the query with a join between CustomerFollowUp and User tables
    #     followup_count_by_assigned_to = (
    #         await db_session.execute(
    #             select(
    #                 CustomerFollowUp.assign_to,
    #                 func.count().label('followup_count'),
    #                 User  # Include the User table in the select statement
    #             )
    #             .select_from(join(CustomerFollowUp, User, join_condition))
    #             .group_by(CustomerFollowUp.assign_to,User)
    #         )
    #     )
    #     results = []
    #     for row in followup_count_by_assigned_to.all():
            
    #         customer_followup_count = row[1]  # SQLAlchemy row object for CustomerFollowUp
    #         user = row[2]  # SQLAlchemy row object for User

    #         result_dict = {
    #             # "assign_to": customer_followup.assign_to,
    #             "followup_count": customer_followup_count,  # Assuming followup_count is an attribute of CustomerFollowUp
    #             # Add other fields from CustomerFollowUp and User as needed
    #             "user_id": user.id,
    #             "user_name": user.first_name
    #         }
    #         results.append(result_dict)
    #     result.update(
    #         {
    #             "followup_count_by_assigned_to": results              
    #         }
    #     )
    
    return  result

