from fastapi import FastAPI


from .routers import users, auth , customers, branches


app = FastAPI()


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(branches.router)