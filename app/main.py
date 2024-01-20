from fastapi import FastAPI


from .routers import users, auth , customers, branches, products, test_request_forms


app = FastAPI()


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(branches.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(test_request_forms.router)