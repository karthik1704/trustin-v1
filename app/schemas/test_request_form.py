

from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from ..models.test_request_forms import SamplingByEnum, TestingDetail, YesOrNoEnum, ReportSentByEnum, DocumentsTypeEnum, TestingProcessEnum, DisposalProcessEnum

class TestDetail(BaseModel):

    priority_order : int
    parameter_id : int

    class Meta:
        orm_model=TestingDetail



class TRFCreate(BaseModel):


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

    test_types_ids: List[int]
    testing_details: List[TestDetail]

class TestDetailCreate(BaseModel):

    priority_order : int
    trf_id : int
    parameter_id : int


class TRFSchema(BaseModel):
    sample_id : Optional[str]
    sample_name : Optional[str]
    description : Optional[str]
    manufactured_by : Optional[str]
    batch_or_lot_no : Optional[str]
    manufactured_date : Optional[date]
    expiry_date : Optional[date]
    batch_size : Optional[int]
    format_name : Optional[str]
    nabl_logo : Optional[bool]
    no_of_samples : Optional[int]
    sample_storage_condition : Optional[str]
    sampling_by : Optional[SamplingByEnum]
    # testing_process : List[TestingProcessEnum]
    # report_sent_by : List[ReportSentByEnum]
    # sample_disposal_process :DisposalProcessEnum
    # fail_statement_sent :YesOrNoEnum
    # specific_decision_rule :YesOrNoEnum
    # binary_decision_rule :YesOrNoEnum
    # submission_of_documents :List[DocumentsTypeEnum]