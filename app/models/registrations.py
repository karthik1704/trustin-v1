from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    func,
    UUID,
    Enum,
    Date,
    DateTime,
)
from typing import Any, List, Optional
from datetime import date, datetime

# from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column, Mapped, relationship, joinedload, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models import Base, Branch, TRF, Customer, TestingParameter, TestType
from pydantic import BaseModel, ConfigDict, ValidationError
from enum import Enum as PyEnum

from app.models.samples import Product
from app.utils import get_unique_code
from .users import User


class TestingProcessEnum(PyEnum):
    BATCH_ANALYSIS = "BATCH_ANALYSIS"
    METHOD_DEVELOPMENT = "METHOD_DEVELOPMENT"
    METHOD_VALIDATION = "METHOD_VALIDATION"
    RD_RESEARCH = "RD_RESEARCH"
    REGULATORY = "REGULATORY"


class DisposalProcessEnum(PyEnum):
    DISCARD = "DISCARD"
    RETURN = "RETURN"


class ReportSentByEnum(PyEnum):
    COURIER = "COURIER"
    EMAIL = "EMAIL"


class SamplingByEnum(PyEnum):
    CUSTOMER = "CUSTOMER"
    LABORATORY = "LABORATORY"


class YesOrNoEnum(PyEnum):
    YES = "YES"
    NO = "NO"


class Registration(Base):
    __tablename__ = "registrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String, nullable=True)
    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey(Branch.id))
    trf_id: Mapped[int] = mapped_column(Integer, ForeignKey(TRF.id), nullable=True)
    trf_code: Mapped[Optional[str]]
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey(Customer.id))
    test_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey(TestType.id))
    company_name: Mapped[str] = mapped_column(String)
    customer_address_line1: Mapped[str] = mapped_column(String)
    customer_address_line2: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String)
    pincode_no: Mapped[str] = mapped_column(String)
    gst: Mapped[str] = mapped_column(String)
    date_of_registration: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    date_of_received: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # test_type  : Mapped[str] =  mapped_column(String)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))

    testing_process: Mapped[TestingProcessEnum]

    nabl_logo: Mapped[Optional[bool]]
    license_no: Mapped[Optional[str]]
    sampled_by: Mapped[Optional[SamplingByEnum]]

    sample_disposal_process: Mapped[Optional[DisposalProcessEnum]]
    sample_name: Mapped[Optional[str]]
    batch_or_lot_no: Mapped[Optional[str]]
    manufactured_date: Mapped[Optional[date]]
    expiry_date: Mapped[Optional[date]]
    batch_size: Mapped[Optional[int]]
    received_quantity: Mapped[Optional[int]]

    no_of_samples: Mapped[int] = mapped_column(default=0)
    controlled_quantity: Mapped[Optional[int]] = mapped_column(default=0)
    reports_send_by: Mapped[Optional[ReportSentByEnum]]

    trf = relationship("TRF", back_populates="registrations", lazy="selectin")
    # batches = relationship("Batch", back_populates="registration", lazy="selectin")
    test_params = relationship(
        "RegistrationTestParameter", back_populates="registration", lazy="selectin"
    )
    test_types = relationship(
        "RegistrationTestType", back_populates="registration", lazy="selectin"
    )
    samples = relationship("Sample", back_populates="registration", lazy="selectin")
    product_data = relationship(
        "Product", back_populates="registrations", lazy="selectin"
    )

    @classmethod
    async def generate_next_code(cls, database_session):

        _stmt = (
            select(cls.code)
            .where(*[])
            .order_by(
                desc(cls.code)
            )  # Assuming `code` is the column you want to order by
        )
        _result = await database_session.execute(_stmt)
        highest_code = _result.scalars().first()
        if highest_code:
            highest_code_int = int(highest_code.split("/")[-1]) + 1
        else:
            highest_code_int = 1
        # Generate the new code by combining the prefix and the incremented integer
        new_code = get_unique_code(
            "REG", highest_code_int
        )  # Adjust the format based on your requirements
        # session.close()
        return new_code

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions).order_by(desc(cls.code))
        _result = await database_session.execute(_stmt)
        return _result.scalars()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    def update_registration(self, updated_data):

        for field, value in updated_data.items():
            setattr(self, field, value) if value else None

    async def update_batches(
        self, database_session: AsyncSession, batches_data, current_user
    ):
        print("update batches")
        time = datetime.now()
        for batch_data in batches_data:
            batch_id = batch_data.pop("id", None)
            batch = None
            if batch_id:
                batch = await Batch.get_one(database_session, [Batch.id == batch_id])
                print(batch)
            if batch:
                print("u[date]")
                update_dict = {
                    "updated_at": time,
                    "updated_by": current_user["id"],
                }
                batch_data = {**batch_data, **update_dict}
                batch.update_batch(batch_data)
            else:
                print("create")
                print(batch_data)

                update_dict = {
                    "created_at": time,
                    "updated_at": time,
                    "created_by": current_user["id"],
                    "updated_by": current_user["id"],
                }
                batch_data = {**batch_data, **update_dict}
                batch = Batch(**batch_data, registration_id=self.id)
                Batch.create_batch(database_session, batch)

    async def update_test_prams(
        self, database_session: AsyncSession, test_params_data, current_user
    ):
        print("update test params")
        time = datetime.now()
        for test_param_data in test_params_data:
            test_param_id = test_param_data.get("test_params_id", None)
            test_param = None
            if test_param_id:
                test_param = await RegistrationTestParameter.get_one(
                    database_session,
                    [
                        RegistrationTestParameter.registration_id == self.id,
                        RegistrationTestParameter.test_params_id == test_param_id,
                    ],
                )
                print(test_param)
            if test_param:
                print("u[date]")
                update_dict = {
                    "updated_at": time,
                    "updated_by": current_user["id"],
                }
                test_param_data = {**test_param_data, **update_dict}
                test_param.update_registration_test_param(test_param_data)
            else:
                print("create")
                print(test_param_data)

                update_dict = {
                    "created_at": time,
                    "updated_at": time,
                    "created_by": current_user["id"],
                    "updated_by": current_user["id"],
                }
                test_param_data = {**test_param_data, **update_dict}
                test_param = RegistrationTestParameter(
                    **test_param_data, registration_id=self.id
                )
                RegistrationTestParameter.create_registration_test_param(
                    database_session, test_param
                )
        existing_params = await RegistrationTestParameter.get_all(
            database_session, [RegistrationTestParameter.registration_id == self.id]
        )
        for existing_param in existing_params:
            for test_param_data in test_params_data:
                if existing_param.test_params_id == test_param_data.get(
                    "test_params_id", ""
                ):
                    break
            else:
                await database_session.delete(existing_param)

    async def update_samples(
        self, database_session: AsyncSession, samples_data, current_user, reg_params
    ):
        print("update test params")
        time = datetime.now()
        for sample_data in samples_data:
            sample_id = sample_data.get("id", None)
            reg_sample = None
            if sample_id:

                reg_sample = await Sample.get_one(
                    database_session,
                    [
                        Sample.registration_id == self.id,
                        Sample.id == sample_id,
                    ],
                )
                print(reg_sample)
            if reg_sample:
                print("u[date]")
                update_dict = {
                    "updated_at": time,
                    "updated_by": current_user["id"],
                }
                sample_data = {**sample_data, **update_dict}
                await reg_sample.update_sample(sample_data)

                await reg_sample.update_test_params(
                    database_session, reg_params, current_user
                )
                # for params_data in reg_params:
                #     param_id = params_data["test_params_id"]
                #     params_data = {
                #         "order": params_data.get("order"),
                #         **update_dict,
                #     }
                #     print(params_data)
                #     test_param = await SampleTestParameter.get_one(
                #         database_session,
                #         [
                #             SampleTestParameter.test_parameter_id == param_id,
                #             SampleTestParameter.sample_id == reg_sample.id,
                #         ],
                #     )
                #     await test_param.update_sample_test_param(params_data)

            else:
                print("create")
                print(sample_data)

                update_dict = {
                    "status_id": 1,
                    "assigned_to": current_user["id"],
                    "created_at": time,
                    "updated_at": time,
                    "created_by": current_user["id"],
                    "updated_by": current_user["id"],
                }
                sample_data = {**sample_data, **update_dict}
                sample_id = await Sample.generate_next_code(database_session)
                sample_data.update({"sample_id": sample_id})
                reg_sample = Sample(**sample_data, registration_id=self.id)
                database_session.add(reg_sample)
                await database_session.commit()
                await database_session.refresh(reg_sample)
                for params_data in reg_params:
                    update_dict = {
                        "created_at": time,
                        "updated_at": time,
                        "created_by": current_user["id"],
                        "updated_by": current_user["id"],
                    }
                    test_data = {
                        "test_parameter_id": params_data["test_params_id"],
                        **update_dict,
                    }
                    print(params_data)
                    test_param = SampleTestParameter(
                        **test_data,
                        order=params_data.get("order"),
                        sample_id=reg_sample.id,
                    )
                    database_session.add(test_param)
                    await database_session.commit()

        existing_samples = await Sample.get_all(
            database_session, [Sample.registration_id == self.id]
        )
        for sample in existing_samples:
            for sample_data in samples_data:
                if sample_data.get(id) is None:
                    break
                if sample.id == sample_data.get("id", ""):
                    break
            else:
                await database_session.delete(sample)

    async def update_test_types(
        self, database_session: AsyncSession, test_types_data, current_user
    ):
        print("update test types")
        time = datetime.now()
        print(test_types_data)
        for test_type_data in test_types_data:
            test_type_id = test_type_data.get("test_type_id", None)
            test_type = None
            if test_type_id:
                test_type = await RegistrationTestType.get_one(
                    database_session,
                    [
                        RegistrationTestType.registration_id == self.id,
                        RegistrationTestType.test_type_id == test_type_id,
                    ],
                )
                # print(test_param)
            if test_type:
                print("u[date]")
                update_dict = {
                    "updated_at": time,
                    "updated_by": current_user["id"],
                }
                test_type_data = {**test_type_data, **update_dict}
                test_type.update_registration_test_type(test_type_data)
            else:
                print("create")
                print(test_type_data)

                update_dict = {
                    "created_at": time,
                    "updated_at": time,
                    "created_by": current_user["id"],
                    "updated_by": current_user["id"],
                }
                test_type_data = {**test_type_data, **update_dict}
                test_type = RegistrationTestType(
                    **test_type_data, registration_id=self.id
                )
                RegistrationTestType.create_registration_test_type(
                    database_session, test_type
                )
        existing_types = await RegistrationTestType.get_all(
            database_session, [RegistrationTestType.registration_id == self.id]
        )
        for existing_type in existing_types:
            for test_type_data in test_types_data:
                if existing_type.test_type_id == test_type_data.get("test_type_id", ""):
                    break
            else:
                await database_session.delete(existing_type)


class Batch(Base):
    __tablename__ = "batches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # name : Mapped[str]= mapped_column(String)
    # registration_id  : Mapped[int]  = mapped_column(Integer, ForeignKey(Registration.id))
    customer_id: Mapped[int] = mapped_column(ForeignKey(Customer.id), nullable=True)
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id), nullable=True)
    batch_no: Mapped[str] = mapped_column(String)
    manufactured_date: Mapped[Date] = mapped_column(Date)
    expiry_date: Mapped[Date] = mapped_column(Date)
    batch_size: Mapped[int] = mapped_column(Integer)
    received_quantity: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # registration = relationship("Registration", back_populates="batches")
    # sample_batch = relationship("Sample", back_populates="batch", lazy="selectin")
    product: Mapped["Product"] = relationship(back_populates="batch", lazy="selectin")
    customer: Mapped["Customer"] = relationship(
        back_populates="batches", lazy="selectin"
    )

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions).order_by(desc(cls.id))
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    @classmethod
    def create_batch(cls, db: AsyncSession, batch):
        db.add(batch)

    def update_batch(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)


class RegistrationTestParameter(Base):
    __tablename__ = "registration_test_parameters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # name : Mapped[str]= mapped_column(String)
    registration_id: Mapped[int] = mapped_column(Integer, ForeignKey(Registration.id))
    test_params_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(TestingParameter.id)
    )
    order: Mapped[Optional[int]]
    quantity: Mapped[Optional[int]]
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    registration = relationship(
        "Registration", back_populates="test_params", lazy="selectin"
    )
    test_parameter = relationship(
        "TestingParameter",
        back_populates="registration_test_parameters",
        lazy="selectin",
    )

    # model_config = ConfigDict(from_attributes=True)

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    @classmethod
    def create_registration_test_param(cls, db: AsyncSession, batch):
        db.add(batch)

    def update_registration_test_param(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)


class RegistrationTestType(Base):
    __tablename__ = "registration_test_types"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # name : Mapped[str]= mapped_column(String)
    registration_id: Mapped[int] = mapped_column(Integer, ForeignKey(Registration.id))
    test_type_id: Mapped[int] = mapped_column(Integer, ForeignKey(TestType.id))
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    registration = relationship(
        "Registration", back_populates="test_types", lazy="selectin"
    )
    test_type = relationship(
        "TestType", back_populates="registration_test_types", lazy="selectin"
    )
    # test_type = relationship("TestType", back_populates="registration_test_types",  lazy="selectin")
    # model_config = ConfigDict(from_attributes=True)

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    @classmethod
    def create_registration_test_type(cls, db: AsyncSession, batch):
        db.add(batch)

    def update_registration_test_type(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)


class SampleStatus(Base):
    __tablename__ = "sample_status"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=True
    )
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    sample = relationship("Sample", back_populates="status_data", lazy="selectin")
    sample_history_from = relationship(
        "SampleHistory",
        back_populates="from_status",
        foreign_keys="[SampleHistory.from_status_id]",
    )
    sample_history_to = relationship(
        "SampleHistory",
        back_populates="to_status",
        foreign_keys="[SampleHistory.to_status_id]",
    )
    sample_workflow_status = relationship(
        "SampleWorkflow", back_populates="sample_status", lazy="selectin"
    )
    # ["Draft", "Review Pending", "Requested","Received","Under Testing", "Verification Pending", "Done"]

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions).order_by(cls.id)
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()


class SampleHistory(Base):
    __tablename__ = "sample_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_id: Mapped[int] = mapped_column(Integer, ForeignKey("samples.id"))
    from_status_id: Mapped[int] = mapped_column(Integer, ForeignKey(SampleStatus.id))
    to_status_id: Mapped[int] = mapped_column(Integer, ForeignKey(SampleStatus.id))
    assigned_to: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    comments: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    sample = relationship("Sample", back_populates="sample_history")
    assignee = relationship(
        "User",
        back_populates="sample_history_assignee",
        foreign_keys=[assigned_to],
        lazy="selectin",
    )
    created_by_user = relationship(
        "User",
        back_populates="sample_history_created",
        foreign_keys=[created_by],
        lazy="selectin",
    )
    from_status = relationship(
        "SampleStatus",
        back_populates="sample_history_from",
        foreign_keys=[from_status_id],
        lazy="selectin",
    )
    to_status = relationship(
        "SampleStatus",
        back_populates="sample_history_to",
        foreign_keys=[to_status_id],
        lazy="selectin",
    )


class Sample(Base):
    __tablename__ = "samples"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_id: Mapped[str] = mapped_column(String)
    # name: Mapped[str] = mapped_column(String)
    registration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Registration.id), nullable=True
    )
    # batch_id: Mapped[int] = mapped_column(Integer, ForeignKey(Batch.id))
    # department_id = Column(Integer, ForeignKey("testtypes.id"))
    test_type_id:Mapped[int] = mapped_column(Integer, ForeignKey(TestType.id))

    sample_name: Mapped[Optional[str]]
    batch_or_lot_no: Mapped[Optional[str]]
    manufactured_date: Mapped[Optional[date]]
    expiry_date: Mapped[Optional[date]]
    batch_size: Mapped[Optional[int]]
    received_quantity: Mapped[Optional[int]]

    assigned_to: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("sample_status.id"), nullable=True
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String, default="Draft", nullable=True)

    sample_workflows = relationship(
        "SampleWorkflow",
        back_populates="sample",
        lazy="selectin",
        order_by="SampleWorkflow.id",
    )
    sample_test_parameters = relationship(
        "SampleTestParameter",
        back_populates="sample",
        lazy="selectin",
        order_by="SampleTestParameter.order",
        cascade="all, delete",
    )
    sample_history = relationship(
        "SampleHistory",
        back_populates="sample",
        lazy="selectin",
        order_by=desc(SampleHistory.id),
    )
    status_data = relationship("SampleStatus", back_populates="sample", lazy="selectin")
    assignee = relationship(
        "User",
        back_populates="sample_assignee",
        foreign_keys=[assigned_to],
        lazy="selectin",
    )
    registration = relationship(
        "Registration", back_populates="samples", lazy="selectin"
    )
    # created = relationship("User", back_populates="sample_created",  foreign_keys=[created_by], lazy="selectin")
    # batch = relationship("Batch", back_populates="sample_batch", lazy="selectin")
    # registration_sample: Mapped["RegistrationSample"] = relationship(
    #     back_populates="sample", lazy="selectin", uselist=True
    # )

    @classmethod
    async def generate_next_code(cls, database_session):

        _stmt = (
            select(cls.sample_id)
            .where(*[])
            .order_by(
                desc(cls.sample_id)
            )  # Assuming `code` is the column you want to order by
        )
        _result = await database_session.execute(_stmt)
        highest_code = _result.scalars().first()
        if highest_code:
            highest_code_int = int(highest_code.split(f"/")[-1]) + 1
        else:
            highest_code_int = 1
        # Generate the new code by combining the prefix and the incremented integer
        new_code = get_unique_code(
            "SAM", highest_code_int
        )  # Adjust the format based on your requirements
        # database_session.close()
        return new_code

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions).order_by(desc(cls.id))
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()

    @classmethod
    async def get_for_qa_hod(
        cls, database_session: AsyncSession, user, where_conditions: list[Any]
    ):
        _stmt = (
            select(cls)
            .select_from(cls)
            .join(User, cls.test_type_id == User.qa_type_id)
            .where(User.id == user.get("id"), cls.status == "Submitted")
        )
        # _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars()

    @classmethod
    async def get_for_qa_analyst(
        cls, database_session: AsyncSession, user, where_conditions: list[Any]
    ):
        _stmt = (
            select(cls)
            .distinct()
            .select_from(cls)
            .join(SampleWorkflow, cls.id == SampleWorkflow.sample_id)
            # .join(User, SampleWorkflow.assigned_to == User.sample_id)
            .where(
                SampleWorkflow.assigned_to == user.get("id"), cls.status == "Submitted"
            )
        )
        # _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    async def update_sample(self, updated_data):

        for field, value in updated_data.items():
            setattr(self, field, value) if value else None

    async def update_test_params(
        self, database_session: AsyncSession, test_params_data, current_user
    ):
        print("update test params")
        time = datetime.now()
        for test_param_data in test_params_data:
            test_param_id = test_param_data.get("test_params_id", None)
            test_param = None
            if test_param_id:
                test_param = await SampleTestParameter.get_one(
                    database_session,
                    [
                        SampleTestParameter.sample_id == self.id,
                        SampleTestParameter.test_parameter_id == test_param_id,
                    ],
                )
                print(test_param)
            if test_param:
                print("u[date]")
                update_dict = {
                    "updated_at": time,
                    "updated_by": current_user["id"],
                }
                test_param_data = {**test_param_data, **update_dict}
                await test_param.update_sample_test_param(test_param_data)
            else:
                print("create")
                print(test_param_data)

                update_dict = {
                    "created_at": time,
                    "updated_at": time,
                    "created_by": current_user["id"],
                    "updated_by": current_user["id"],
                }
                test_param_data = {
                    "test_parameter_id": test_param_data.get("test_params_id"),
                    "order": test_param_data.get("order"),
                    **update_dict,
                }
                test_param = SampleTestParameter(**test_param_data, sample_id=self.id)
                SampleTestParameter.create_sample_test_param(
                    database_session, test_param
                )
        existing_params = await SampleTestParameter.get_all(
            database_session, [SampleTestParameter.sample_id == self.id]
        )
        for existing_param in existing_params:
            for test_param_data in test_params_data:
                if existing_param.test_parameter_id == test_param_data.get(
                    "test_params_id", ""
                ):
                    break
            else:
                await database_session.delete(existing_param)

    async def create_workflow(self, db_session, current_user):
        status_list = await SampleStatus.get_all(db_session, [])
        time = datetime.now()
        update_dict = {
            "created_at": time,
            "updated_at": time,
            "created_by": current_user["id"],
            "updated_by": current_user["id"],
        }
        for status in status_list:
            workflow_dict = {
                "sample_id": self.id,
                "sample_status_id": status.id,
                "department_id": status.department_id,
                "role_id": status.role_id,
                "assigned_to": (
                    current_user["id"] if status.name == "Draft" else status.user_id
                ),
                "status": (
                    "Done"
                    if status.name == "Draft"
                    else (
                        "In Progress"
                        if status.name == "Review Pending"
                        else "Yet To Start"
                    )
                ),
            }
            workflow_dict = {**workflow_dict, **update_dict}
            print(workflow_dict)
            workflow = SampleWorkflow(**workflow_dict)
            db_session.add(workflow)
        await db_session.commit()

    async def create_history(self, db_session, current_user, history):
        time = datetime.now()
        update_dict = {
            "created_at": time,
            "created_by": current_user["id"],
        }
        history = {**history, **update_dict}
        history = SampleHistory(**history)
        db_session.add(history)
        await db_session.commit()


class SampleTestParameter(Base):
    __tablename__ = "sample_test_parameters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_id: Mapped[int] = mapped_column(Integer, ForeignKey(Sample.id))
    test_parameter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(TestingParameter.id)
    )
    order: Mapped[int] = mapped_column(Integer, nullable=True)
    quantity: Mapped[Optional[int]]

    test_type: Mapped[str] = mapped_column(String, nullable=True)
    value: Mapped[str] = mapped_column(String, nullable=True)
    result: Mapped[bool] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    sample = relationship(
        "Sample", back_populates="sample_test_parameters", lazy="selectin"
    )
    test_parameter = relationship(
        "TestingParameter", back_populates="sample_test_parameters", lazy="selectin"
    )

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    @classmethod
    def create_sample_test_param(cls, db: AsyncSession, test_params):
        db.add(test_params)

    async def update_sample_test_param(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)


class SampleWorkflow(Base):
    __tablename__ = "sample_workflows"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sample_id: Mapped[int] = mapped_column(Integer, ForeignKey(Sample.id))
    sample_status_id: Mapped[int] = mapped_column(Integer, ForeignKey(SampleStatus.id))
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=True
    )
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=True)
    assigned_to: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String, server_default="Yet to start")

    sample = relationship("Sample", back_populates="sample_workflows")
    assignee = relationship(
        "User",
        back_populates="sample_workflow_assignee",
        foreign_keys=[assigned_to],
        lazy="selectin",
    )
    department = relationship(
        "Department", back_populates="sample_workflow_department", lazy="selectin"
    )
    role = relationship("Role", back_populates="sample_workflow_role", lazy="selectin")
    sample_status = relationship(
        "SampleStatus", back_populates="sample_workflow_status", lazy="selectin"
    )

    # sample_workflow_history= relationship("SampleRequestHistory", back_populates="sample_request")

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        print("where_conditions", *where_conditions)
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    async def update_workflow(self, updated_data):
        for field, value in updated_data.items():
            print(self.id, field, value)
            setattr(self, field, value) if value else None


class RegistrationSample(Base):
    __tablename__ = "registration_sample"
    id: Mapped[int] = mapped_column(primary_key=True)
    registration_id = mapped_column(ForeignKey(Registration.id), nullable=True)
    sample_id = mapped_column(ForeignKey(Sample.id), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    # sample: Mapped["Sample"] = relationship(
    #     back_populates="registration_sample", lazy="selectin"
    # )
    # registration: Mapped["Registration"] = relationship(back_populates="reg_samples")

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    @classmethod
    def create_registration_sample(cls, db: AsyncSession, samples):
        db.add(samples)

    async def update_reg_sample(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)
