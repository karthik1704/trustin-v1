from datetime import date
import decimal
from token import OP
from typing import List

# from pydantic import BaseModel
# from ..models.test_request_forms import SamplingByEnum, TestingDetail, YesOrNoEnum, ReportSentByEnum, DocumentsTypeEnum, TestingProcessEnum, DisposalProcessEnum

from pydantic import BaseModel, field_validator, validator
from typing import List, Optional
from datetime import datetime

from app.schemas.customers import CustomerSchema
from ..models.registrations import (
    DisposalProcessEnum,
    Registration,
    Batch,
    RegistrationStatus,
    ReportSentByEnum2,
    SamplingByEnum,
    TestingProcessEnum,
)
from ..schemas.users import DepartmentSchema, UserSchema, RoleSchema
from ..schemas.test_request_form import TRFSchema
from ..schemas.samples import ProductSchema

# from .samples import TestParameterCreate


class BatchSchema(BaseModel):
    id: int
    # registration_id: int
    batch_no: str
    manufactured_date: datetime
    expiry_date: datetime
    batch_size: int
    received_quantity: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    product_id: Optional[int]
    customer_id: Optional[int]
    product: Optional[ProductSchema]
    customer: Optional[CustomerSchema]


class TestParameterSchema(BaseModel):
    id: int
    # branch_id: int 
    test_type_id: int
    product_id: Optional[int]
    customer_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    parameter_code: Optional[str]
    testing_parameters: Optional[str]
    amount: Optional[float]
    method_or_spec: Optional[str]
    group_of_test_parameters: str | None


class TestTypeSchema(BaseModel):
    id: int
    name: str


class RegistrationTestParamsSchema(BaseModel):
    id: int
    registration_id: int
    test_params_id: int
    order:int
    quantity: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    test_parameter: Optional[TestParameterSchema]


class RegistrationTestTypeSchema(BaseModel):
    id: int
    registration_id: int
    test_type_id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    # test_type : Optional[TestTypeSchema]


class RegistrationListSchema(BaseModel):
    id: int
    # branch_id: int
    code: (
        str | None
    )  # added none temp, because code null in already created registration
    # trf_id: int
    # trf_code: str
    company_id: int
    company_name: str
    # customer_address_line1: str
    # customer_address_line2: str
    # city: str
    # state: str
    # pincode_no: str
    gst: str
    date_of_registration: datetime
    date_of_received: datetime
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    # test_type: str
    product_id: int
    status: RegistrationStatus
    

class RegistratinListWithPaginationSchema(BaseModel):
    data: List[RegistrationListSchema]
    page: int
    size: int
    total:int


class RegistrationSampleSchema(BaseModel):
    id: int
    # branch_id: int
    code: (
        str | None
    )  # added none temp, because code null in already created registration
    # trf_code: str
    company_id: int
    company_name: str
    full_address: str
    customer_reference_no: str
    contact_person_name: str
    contact_number: str
    license_no: str
    # customer_address_line1: str
    # customer_address_line2: str
    # city: str
    # state: str
    # pincode_no: str
    product_id:int
    gst: str
    date_of_registration: datetime
    date_of_received: datetime
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    # test_type: str
    product_data: ProductSchema
    

class RegistrationCodeSchema(BaseModel):
    code: str | None
    company_name: str


class SampleTestParameterSchema(BaseModel):
    id: int
    sample_id: int
    order: int | None
    quantity: Optional[int]
    test_parameter_id: int
    test_type: Optional[str]
    value: Optional[str]
    specification_limits: Optional[str]
    result: Optional[bool]
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    test_parameter: Optional[TestParameterSchema]

class SampleTestTypeSchema(BaseModel):
    id: int
    sample_id: Optional[int]
    test_type_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    test_type: Optional[TestTypeSchema]


class SampleStatusSchema(BaseModel):
    id: int
    name: str


class SampleWorkflowSchema(BaseModel):
    id: int
    sample_status_id: int
    assigned_to: Optional[int]
    test_type_id: Optional[int]
    status: str
    assignee: Optional[UserSchema]
    department: Optional[DepartmentSchema]
    role: Optional[RoleSchema]
    sample_status: Optional[SampleStatusSchema]
    updated_at: datetime


class SampleHistorySchema(BaseModel):
    id: int
    test_type : Optional[TestTypeSchema]
    from_status_id: int
    to_status_id: int
    assigned_to: Optional[int]
    comments: Optional[str]
    created_at: datetime
    created_by: int
    from_status: Optional[SampleStatusSchema]
    to_status: Optional[SampleStatusSchema]
    assignee: Optional[UserSchema]
    created_by_user: Optional[UserSchema]


class SampleListSchema(BaseModel):
    id: int
    sample_id: str
    sample_name: str
    batch_or_lot_no: str
    manufactured_date: Optional[str]
    expiry_date: Optional[str]
    tat:Optional[date] 
    batch_size: Optional[str]
    received_quantity: str
    registration_id: int | None
    status_id: Optional[int]
    test_type_id: Optional[int]
    assigned_to: Optional[int]
    # batch_id: int
    status: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    registration: Optional[RegistrationCodeSchema | None]
    # batch: Optional[BatchSchema]
    status_data: Optional[SampleStatusSchema]
    sample_test_types: Optional[list[SampleTestTypeSchema]]

class SampleListWithPaginationSchema(BaseModel):
    data: List[SampleListSchema]
    total: int
    page: int
    size: int

class SampleDetailSchema(BaseModel):

    id: int
    sample_id: int
    test_type_id: int
    assigned_to: Optional[int]
    testing_start_date: Optional[date]
    testing_end_date: Optional[date]
    sample_issued:Optional[int]
    issued_to:Optional[str]
    samples_received:Optional[bool]
    assignee: Optional[UserSchema]
    authorized_sign_id: Optional[int]
    authorized_sign: Optional[UserSchema]

    # received_quantity: Optional[int]


class SampleSchema(BaseModel):
    id: int
    sample_id: str
    sample_name: str
    batch_or_lot_no: str
    manufactured_date: Optional[str]
    expiry_date: Optional[str]
    testing_start_date: Optional[date]
    testing_end_date: Optional[date]
    tat:Optional[date]
    description: Optional[str]
    sample_issued:Optional[int]
    issued_to:Optional[str]
    sample_condition:Optional[str]
    sterilization_batch_no:Optional[str]
    under_cdsco:Optional[bool]
    samples_received:Optional[bool]
    nabl_logo:Optional[bool]
    batch_size: Optional[str]
    received_quantity: str
    registration_id: int | None
    status_id: Optional[int]
    test_type_id: Optional[int]
    assigned_to: Optional[int]
    ulr_no: Optional[str]
    report_no: Optional[str]
    discipline:Optional[str]
    group:Optional[str]
    # batch_id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    status: Optional[str]
    sample_test_parameters: Optional[list[SampleTestParameterSchema]]
    sample_test_types: Optional[list[SampleTestTypeSchema]]
    sample_workflows: Optional[list[SampleWorkflowSchema]]
    sample_history: Optional[list[SampleHistorySchema]]
    status_data: Optional[SampleStatusSchema]
    assignee: Optional[UserSchema]
    # batch: Optional[BatchSchema]
    registration: Optional[RegistrationSampleSchema]
    sample_detail: Optional[List[SampleDetailSchema]]


class RegistrationSamplesSchema(BaseModel):
    id: int
    registration_id: int
    sample_id: int

    sample: Optional[SampleSchema]


class RegSamples(BaseModel):
    id: int
    sample_id: str
    sample_name: str
    test_type_id: Optional[int]
    batch_or_lot_no: str
    description: str
    manufactured_date: Optional[str]
    expiry_date: Optional[str]
    tat: Optional[date]
    batch_size: Optional[str]
    received_quantity: str
    sample_condition:Optional[str]
    sterilization_batch_no:Optional[str]
    status_id: int
    sample_test_parameters: Optional[list[SampleTestParameterSchema]]
    sample_test_types: Optional[list[SampleTestTypeSchema]]
    


class RegistrationSchema(BaseModel):
    id: int
    code: str
    # branch_id: int
    front_desk_id:int
    # trf_code: str
    company_id: int
    company_name: str
    full_address: str
    # customer_address_line1: str
    # customer_address_line2: str
    # city: str
    # state: str
    # pincode_no: str
    customer_reference_no: Optional[str]
    contact_person_name:Optional[str]
    contact_email: Optional[str]
    contact_number: Optional[str]
    gst: str
    date_of_registration: datetime
    date_of_received: datetime
    created_at: datetime
    updated_at: datetime
    created_by: int
    updated_by: int
    # test_type: str
    product_id: int
    # test_type_id: int
    license_no: str
    # nabl_logo: bool
    testing_process: TestingProcessEnum
    sampled_by: SamplingByEnum
    sample_disposal_process: DisposalProcessEnum
    reports_send: ReportSentByEnum2
    # sample_name: str
    # batch_or_lot_no: str
    # manufactured_date: date
    # expiry_date: date
    # batch_size: int
    # received_quantity: int
    # no_of_samples: int
    no_of_batches: int
    # controlled_quantity: int
    # batches : Optional[list[BatchSchema]]
    # test_params: Optional[list[RegistrationTestParamsSchema]]
    samples: Optional[list[RegSamples]]
    status: RegistrationStatus
    # test_types: Optional[list[RegistrationTestTypeSchema]]
    # trf : TRFSchema
    # reg_samples:Optional[List[RegistrationSamplesSchema]]


class BatchCreate(BaseModel):
    batch_no: str
    manufactured_date: date
    expiry_date: date
    batch_size: int
    product_id: Optional[int]
    customer_id: Optional[int]
    received_quantity: int


class RegistrationTestParamsCreate(BaseModel):
    test_params_id: int
    order: int
    quantity: int


class RegistrationTestTypeCreate(BaseModel):
    test_type_id: int


class RegistrationSampleCreate(BaseModel):
    sample_id: int

class SampleTestParams(BaseModel):
    test_parameter_id: int
    order: int

class SampleCreateSchema(BaseModel):
    sample_name: str
    batch_or_lot_no: str
    manufactured_date: Optional[str] 
    expiry_date: Optional[str] 
    tat: Optional[date] | None
    description: Optional[str]
    batch_size: Optional[str]
    received_quantity: str
    # test_type_id: int
    # sample_issued:int
    # issued_to:str
    sample_condition: str
    sterilization_batch_no: str
    test_params: List[SampleTestParams]
    test_types : List[int]


    @staticmethod
    def handle_empty_string(value: Optional[str]):
        if value == "":
            return None
        return value

    @field_validator('manufactured_date', 'expiry_date', 'tat',  mode='before')
    def check_empty_string(cls, value):
        return cls.handle_empty_string(value)
    
class RegistrationCreate(BaseModel):
    # branch_id: int
    # trf_code: str
    company_id: int
    front_desk_id: int
    # test_type_id: int
    company_name: str
    full_address: str
    # customer_address_line1: str
    # customer_address_line2: str
    # city: str
    # state: str
    # pincode_no: str
    customer_reference_no: Optional[str]
    contact_person_name:Optional[str]
    contact_email: Optional[str]
    contact_number: Optional[str]
    gst: str
    date_of_received: date
    product_id: int
    reports_send: ReportSentByEnum2
    license_no: str
    # nabl_logo: bool
    testing_process: TestingProcessEnum
    sampled_by: SamplingByEnum
    sample_disposal_process: DisposalProcessEnum
    status: RegistrationStatus
    # sample_name: str
    # batch_or_lot_no: str
    # manufactured_date: date
    # expiry_date: date
    # batch_size: int
    # received_quantity: int
    # controlled_quantity: int

    # no_of_samples: int
    no_of_batches: int
    # micro_params: List[RegistrationTestParamsCreate]
    # mech_params: List[RegistrationTestParamsCreate]
    samples: List[SampleCreateSchema]
    # batches: List[BatchCreate]
    # test_types : List[RegistrationTestTypeCreate]
    # registration_samples : List[RegistrationSampleCreate]


# class RegistrationWithBatchesCreate(BaseModel):
#     registration: RegistrationCreate
#     batches: List[BatchCreate]


class BatchUpdate(BaseModel):
    # id: Optional[int]
    batch_no: Optional[str]
    manufactured_date: Optional[date]
    expiry_date: Optional[date]
    batch_size: Optional[str]
    product_id: Optional[int]
    customer_id: Optional[int]
    received_quantity: Optional[int]


class RegistrationTestParamsUpdate(BaseModel):
    test_params_id: Optional[int]


class RegistrationTestTypeUpdate(BaseModel):
    test_type_id: Optional[int]


class RegistrationSampleUpdate(BaseModel):
    sample_id: Optional[int]


class SampleTestParamsUpdate(BaseModel):
    test_params_id:int
    order: int

class SampleUpdateSchema(BaseModel):
    id: int | str
    sample_name: str
    batch_or_lot_no: str
    manufactured_date: Optional[str]
    expiry_date: Optional[str]
    tat: Optional[date]
    description: Optional[str]
    batch_size: Optional[str]
    received_quantity: str
    # test_type_id: Optional[int]
    test_types:Optional[List[int]]
    # sample_issued:int
    # issued_to:str
    sample_condition: str
    sterilization_batch_no: str
    test_params: List[SampleTestParamsUpdate]

    
    @staticmethod
    def handle_empty_string(value: Optional[str]):
        if value == "":
            return None
        return value

    @field_validator('manufactured_date', 'expiry_date', 'tat',  mode='before')
    def check_empty_string(cls, value):
        return cls.handle_empty_string(value)


class RegistrationUpdate(BaseModel):
    # branch_id: Optional[int]
    # trf_id: Optional[int]
    # trf_code: str
    # test_type_id: int
    front_desk_id:int
    company_id: Optional[int]
    company_name: Optional[str]
    full_address: Optional[str]
    # customer_address_line1: Optional[str]
    # customer_address_line2: Optional[str]
    # city: Optional[str]
    # state: Optional[str]
    # pincode_no: Optional[str]
    customer_reference_no: Optional[str]
    contact_person_name:Optional[str]
    contact_email: Optional[str]
    contact_number: Optional[str]
    gst: Optional[str]
    date_of_received: Optional[date]
    product_id: Optional[int]
    reports_send: ReportSentByEnum2
    license_no: str
    # nabl_logo: bool
    testing_process: TestingProcessEnum
    sampled_by: SamplingByEnum
    sample_disposal_process: DisposalProcessEnum
    status: RegistrationStatus
    # sample_name: str
    # batch_or_lot_no: str
    # manufactured_date: date
    # expiry_date: date
    # batch_size: int
    # received_quantity: int
    # controlled_quantity: int

    # no_of_samples: int
    no_of_batches: int
    # micro_params: List[RegistrationTestParamsCreate]
    # mech_params: List[RegistrationTestParamsCreate]
    samples: List[SampleUpdateSchema]
    # created_by: Optional[int]
    # updated_by: Optional[int]
    # test_type: Optional[str]
    # batches: Optional[List[BatchUpdate]]
    # test_params: Optional[List[RegistrationTestParamsUpdate]]
    # test_types: Optional[List[RegistrationTestTypeUpdate]]
    # registration_samples: Optional[List[RegistrationSampleUpdate]]


# class RegistrationWithBatchesUpdate(BaseModel):
#     registration: Optional[RegistrationUpdate]
#     batches: Optional[List[BatchUpdate]]

# class RegistrationWithBatchesGet(BaseModel):
#     registration: Optional[RegistrationSchema]
#     batches: Optional[List[BatchSchema]]


class RegistrationWithBatchesGet(BaseModel):
    registrations: Optional[RegistrationSchema]
    # batches: Optional[List[BatchSchema]]


class RegistrationsGet(BaseModel):
    registrations: Optional[RegistrationWithBatchesGet]


class SampleTestParamsCreate(BaseModel):
    test_params_id: int
    order: int
    # test_type  :  Optional[str]


class SampleCreate(BaseModel):
    # sample_id: str
    sample_name: str
    batch_or_lot_no: str
    manufactured_date: date
    expiry_date: date
    batch_size: str
    received_quantity: str
    test_params: list[SampleTestParamsCreate]

class SampleUpdate(BaseModel):
    # sample_id: str
    sample_name: str
    batch_or_lot_no: str
    manufactured_date: str
    expiry_date: str
    batch_size: str
    received_quantity: str
    # sample_issued:int
    # issued_to:str
    sample_condition: str
    sterilization_batch_no: str
    test_params: list[SampleTestParamsCreate]

 

class PatchSampleTestParameterSchema(BaseModel):
    id: int
    order: int
    quantity: Optional[int]=None 
    value: Optional[str]=None
    specification_limits: Optional[str]=None
    result: Optional[bool]=None


class PatchSample(BaseModel):
    testing_start_date: Optional[date] = None
    testing_end_date: Optional[date] = None
    under_cdsco:Optional[bool] = None
    samples_received:Optional[bool] = None
    nabl_logo:Optional[bool] = None
    status: Optional[str] | None
    status_id: Optional[int] | None
    assigned_to: Optional[int] | None = None
    authorized_sign_id: Optional[int] | None = None
    group: Optional[str] = None
    discipline:Optional[str] = None
    comments: Optional[str] | None
    sample_issued:Optional[int] | None = None
    test_type_id:Optional[int] | None = None
    issued_to:Optional[str] | None =None
    test_params: Optional[list[PatchSampleTestParameterSchema]] | None  = None

    @staticmethod
    def handle_empty_string(value: Optional[str]):
        if value == "":
            return None
        return value

    @field_validator('testing_start_date', 'testing_end_date',   mode='before')
    def check_empty_string(cls, value):
        return cls.handle_empty_string(value)