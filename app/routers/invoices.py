from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Path, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import get_current_user
from app.database import get_async_db
from app.models.invoices import Invoice, InvoiceTestParameter

from app.schemas.invoices import InvoiceCreate, InvoiceDetailSchema, InvoiceSchema, InvoiceSchemaWithPagination, InvoiceTestParameterCreate, InvoiceUpdate
from app.schemas.quotations import QuotationCreate, QuotationSchema, QuotationUpdate


router = APIRouter(prefix="/invoices", tags=["Invoices"])

db_dep = Annotated[AsyncSession, Depends(get_async_db)]
user_dep = Annotated[dict, Depends(get_current_user)]

@router.get("/", response_model=Optional[InvoiceSchemaWithPagination])
async def get_all_front_desks_with_pagination(
    db_session: db_dep,
    current_user: user_dep,
    page: int = 1,
    size: int = 10,
    search: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "desc",
):

    try:
        _invoices = await Invoice.get_all_with_pagination(
            db_session,
            [],
            page,
            size,
            search,
            sort_by,
            sort_order,
        )
        return _invoices

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=Optional[InvoiceDetailSchema])
async def get_invoice(id: int, db_session: db_dep, current_user: user_dep):
    try:
        _data = await Invoice.get_one(db_session, [Invoice.id == id])
        return _data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

SGST_RATE = Decimal("0.09")  # 9% SGST
CGST_RATE = Decimal("0.09")  # 9% CGST

@router.post("/", status_code=201)
async def create_invoice(
    data: InvoiceCreate, db_session: db_dep, current_user: user_dep
):
   
    time = datetime.now()
    update_dict = {
        "created_at": time,
        "updated_at": time,
        "created_by": current_user["id"],
        "updated_by": current_user["id"],
    }

    # Prepare invoice data
    invoice_data = data.model_dump()
    invoice_data.update(update_dict)
    parameters = invoice_data.pop("parameters")

    # Calculate sub_total, sgst, cgst, and grand_total
    sub_total = Decimal(0)
    for param_data in parameters:
        total_testing_charge = Decimal(param_data["testing_charge"]) * Decimal(param_data["no_of_tested"])
        sub_total += total_testing_charge

    # Calculate SGST, CGST, and grand_total
    sgst = sub_total * SGST_RATE
    cgst = sub_total * CGST_RATE
    discount = Decimal(invoice_data.get("discount", 0))
    total_after_discount = sub_total - discount
    grand_total = total_after_discount + sgst + cgst

    # Create invoice with calculated values
    invoice_data["sub_total"] = sub_total
    invoice_data["sgst"] = sgst
    invoice_data["cgst"] = cgst
    invoice_data["grand_total"] = grand_total
    invoice_data["discount"] = discount

    # Generate invoice code and create invoice
    code = await Invoice.generate_next_code(db_session)
    invoice_data["invoice_code"] = code
    invoice = Invoice(**invoice_data)
    db_session.add(invoice)
    await db_session.commit()  # Commit to generate the invoice ID

    # Now, create InvoiceTestParameter entries using the generated invoice id
    for param_data in parameters:
        param_data.update(update_dict)
        total_testing_charge = Decimal(param_data["testing_charge"]) * Decimal(param_data["no_of_tested"])
        param_data["total_testing_charge"] = total_testing_charge

        # Create InvoiceTestParameter entry
        test_param = InvoiceTestParameter(
            **param_data,
            invoice_id=invoice.id,  # Now invoice.id is available
        )
        db_session.add(test_param)

    # Final commit to save the InvoiceTestParameter entries
    await db_session.commit()

@router.put("/{id}", response_model=InvoiceSchema)
async def update_quotation(
    id: int, data: InvoiceUpdate, db_session: db_dep, current_user: user_dep
):
    time = datetime.now()
    update_dict = {
        "updated_at": time,
        "updated_by": current_user["id"],
    }

   
    # Fetch the existing invoice
    
    invoice = await Invoice.get_one(db_session, [])

    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Update invoice data
    invoice_data = data.model_dump()
    invoice_data.update(update_dict)
    parameters = invoice_data.pop("parameters")

    for key, value in invoice_data.items():
        setattr(invoice, key, value)

    # Fetch existing parameters
    existing_params = {param.id: param for param in invoice.invoice_test_parameters}

    # Determine parameters to delete
    updated_param_ids = {param_data.get("id") for param_data in parameters if "id" in param_data}
    params_to_delete = [param for param_id, param in existing_params.items() if param_id not in updated_param_ids]

    # Delete missing parameters
    for param in params_to_delete:
        await db_session.delete(param)

    # Update existing or add new parameters
    for param_data in parameters:
        param_id = param_data.get("id")
        if param_id:
            param = existing_params.get(param_id)
            if param:
                # Update existing parameter
                param_data.update(update_dict)
                for key, value in param_data.items():
                    setattr(param, key, value)
            else:
                # Handle case where parameter ID is not found
                raise HTTPException(status_code=404, detail=f"Parameter with ID {param_id} not found")
        else:
            # Create new parameter if no ID is provided
            param_data.update(update_dict)
            new_param = InvoiceTestParameter(
                **param_data,
                invoice_id=invoice.id,
            )
            db_session.add(new_param)

    # Commit all changes in a single transaction
    await db_session.commit()


@router.delete("/{id}")
async def delete_quotation(id: int, db_session: db_dep, current_user: user_dep):

    quotation = await Invoice.get_one(db_session, [Invoice.id == id])
    if quotation is None:
        raise HTTPException(status_code=404, detail="Data not found")

    await db_session.delete(quotation)
    await db_session.commit()
