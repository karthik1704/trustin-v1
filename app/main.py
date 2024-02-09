from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .routers import users, auth , customers, branches, products, test_request_forms, followups, testtype, testparameters
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


origins = [
    "http://localhost",
    "http://localhost:3000",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(branches.router)
app.include_router(customers.router)
app.include_router(followups.router)
app.include_router(products.router)
app.include_router(testtype.router)
app.include_router(testparameters.router)
app.include_router(test_request_forms.router)