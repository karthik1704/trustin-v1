from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import dashboard, departments, pdf
from app.schemas.users import DepartmentSchema


from .routers import (
    users,
    auth,
    customers,
    branches,
    products,
    test_request_forms,
    followups,
    testtype,
    testparameters,
    registrations,
    batches,
    samples,
    roles,
    departments,
    dashboard,
    front_desks,
)
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()


origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://3.109.2.198",
    "http://13.201.194.87",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(roles.router)
app.include_router(departments.router)
app.include_router(auth.router)
app.include_router(branches.router)
app.include_router(customers.router)
app.include_router(followups.router)
app.include_router(products.router)
app.include_router(testtype.router)
app.include_router(testparameters.router)
app.include_router(test_request_forms.router)
app.include_router(registrations.router)
app.include_router(batches.router)
app.include_router(samples.router)
app.include_router(dashboard.router)
app.include_router(front_desks.router)
app.include_router(pdf.router)
