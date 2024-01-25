

from datetime import date
from typing import List
from pydantic import BaseModel
from ..models.test_request_forms import SamplingByEnum, YesOrNoEnum, ReportSentByEnum, DocumentsTypeEnum, TestingProcessEnum, DisposalProcessEnum

class TestDetail(BaseModel):

    priority_order : int
    parameter_id : int



class TRFCreate(BaseModel):

    trf_code : str
    date_of_registration : date
    sample_id : str
    sample_name : str
    description : str
    manufactured_by : str
    batch_or_lot_no : str
    manufactured_date : date
    expiry_date : date
    batch_size :int
    format_name : str
    nabl_logo : bool
    no_of_samples :int
    sample_storage_condition : str

    sampling_by :SamplingByEnum
    testing_process : List[TestingProcessEnum]
    report_sent_by : List[ReportSentByEnum]
    sample_disposal_process :DisposalProcessEnum
    fail_statement_sent :YesOrNoEnum
    specific_decision_rule :YesOrNoEnum
    binary_decision_rule :YesOrNoEnum
    submission_of_documents :List[DocumentsTypeEnum]


    branch_id : int
    product_id : int
    customer_id : int

    test_types_ids: List[int]
    test_details: List[TestDetail]

class TestDetailCreate(BaseModel):

    priority_order : int
    trf_id : int
    parameter_id : int