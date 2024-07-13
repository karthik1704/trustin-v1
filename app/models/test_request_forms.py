from sqlalchemy import (
    ARRAY,
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    DateTime,
    Date,
    Table,
    func,
    Enum,
    Text,
)
from sqlalchemy.orm import relationship
from app.models import Base
from enum import Enum as PyEnum


class TestingProcessEnum(PyEnum):
    BATCH_ANALYSIS = "BATCH_ANALYSIS"
    METHOD_DEVELOPMENT = "METHOD_DEVELOPMENT"
    METHOD_VALIDATION = "METHOD_VALIDATION"
    RD_RESEARCH = "RD_RESEARCH"
    REGULATORY = "REGULATORY"


class SamplingByEnum(PyEnum):
    CUSTOMER = "CUSTOMER"
    LABORATORY = "LABORATORY"


class DisposalProcessEnum(PyEnum):
    DISCARD = "DISCARD"
    RETURN = "RETURN"


class ReportSentByEnum(PyEnum):
    COURIER = "COURIER"
    EMAIL = "EMAIL"
    


class YesOrNoEnum(PyEnum):
    YES = "YES"
    NO = "NO"


class DocumentsTypeEnum(PyEnum):
    MSDS = "MSDS"
    COA = "COA"
    IFU = "IFU"
    IF_ANY_OTHER = "IF_ANY_OTHER"


# many to many intermediate table
testtype_association_table = Table(
    "testtype_association",
    Base.metadata,
    Column("test_type_id", Integer, ForeignKey("testtypes.id")),
    Column("trf_id", Integer, ForeignKey("test_request_forms.id")),
)


class TRF(Base):
    __tablename__ = "test_request_forms"
    id = Column(Integer, primary_key=True)

    trf_code = Column(String)
    date_of_registration = Column(Date())
    sample_id = Column(String)
    sample_name = Column(String)
    description = Column(Text)
    manufactured_by = Column(String)
    batch_or_lot_no = Column(String)
    manufactured_date = Column(Date)
    expiry_date = Column(Date)
    batch_size = Column(Integer)
    format_name = Column(String)
    nabl_logo = Column(Boolean)
    no_of_samples = Column(Integer)
    sample_storage_condition = Column(Text)

    sampling_by = Column(Enum(SamplingByEnum))
    testing_process = Column(ARRAY(Enum(TestingProcessEnum)), default=[])
    report_sent_by = Column(ARRAY(Enum(ReportSentByEnum)), default=[])
    sample_disposal_process = Column(Enum(DisposalProcessEnum))
    fail_statement_sent = Column(Enum(YesOrNoEnum))
    specific_decision_rule = Column(Enum(YesOrNoEnum))
    binary_decision_rule = Column(Enum(YesOrNoEnum))
    submission_of_documents = Column(ARRAY(Enum(DocumentsTypeEnum)), default=[])

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    branch_id = Column(Integer, ForeignKey("branches.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))

    # branch = relationship("Branch", back_populates="trfs")
    product = relationship("Product", back_populates="trfs")
    customer = relationship("Customer", back_populates="trfs")
    followup = relationship(
        "CustomerFollowUp", back_populates="trf"
    )  # one to one relationship
    test_types = relationship(
        "TestType", secondary=testtype_association_table, back_populates="trfs"
    )  # many to many
    test_details = relationship("TestingDetail", back_populates="trf", order_by="TestingDetail.priority_order")
    registrations = relationship("Registration", back_populates="trf")

    @classmethod
    def generate_next_code(cls,database_session ):
        # session = Session()
        # Query the database for the highest existing code
        highest_code = database_session.query(cls.trf_code).order_by(cls.trf_code.desc()).first()
        if highest_code:
            highest_code_int = int(highest_code[0].split("TRF")[-1]) + 1
        else:
            highest_code_int = 1
        # Generate the new code by combining the prefix and the incremented integer
        new_code = f"{'TRF'}{highest_code_int:04}"  # Adjust the format based on your requirements
        # session.close()
        return new_code


class TestingDetail(Base):
    __tablename__ = "testing_detail"
    id = Column(Integer, primary_key=True)
    priority_order = Column(Integer, nullable=False)

    trf_id = Column(Integer, ForeignKey("test_request_forms.id"))
    parameter_id = Column(Integer, ForeignKey("testingparameters.id"))
    trf = relationship("TRF", back_populates="test_details")
    parameter = relationship("TestingParameter", back_populates="test_details")
