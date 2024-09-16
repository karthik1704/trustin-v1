from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Path, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.auth import get_current_user
from app.database import get_async_db
from app.models.invoices import Invoice, InvoiceTestParameter, InvoiceWorkflow

from app.schemas.invoices import (
    InvoiceCreate,
    InvoiceDetailSchema,
    InvoiceSchema,
    InvoiceSchemaWithPagination,
    InvoiceTestParameterCreate,
    InvoiceUpdate,
    PatchInvoice,
)
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
IGST_RATE = Decimal("0.18")  # 18% IGST
PERFORMA_SGST_RATE = Decimal("0.18")  # 18% SGST
PERFORMA_CGST_RATE = Decimal("0.18")  # 18% CGST


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

    extra_dict = {
        "status_id": 1,
        # "assigned_to": current_user["id"],
    }

    # Prepare invoice data
    invoice_data = data.model_dump()
    invoice_data.update(update_dict)
    invoice_data.update(extra_dict)
    parameters = invoice_data.pop("parameters")

    # Calculate sub_total, sgst, cgst, and grand_total
    sub_total = Decimal(0)
    for param_data in parameters:
        total_testing_charge = Decimal(param_data["testing_charge"]) * Decimal(
            param_data["no_of_tested"]
        )
        sub_total += total_testing_charge

    # Calculate SGST, CGST, discount, and grand_total based on invoice_type
    discount = Decimal(invoice_data.get("discount", 0))
    print(invoice_data.get("invoice_type"))
    # Calculate totals based on invoice_type
    if invoice_data.get("invoice_mode") == "INVOICE":
        if invoice_data.get("invoice_type") == "EXEMPTED_CUSTOMER":
            sgst = Decimal(0)
            cgst = Decimal(0)
            igst = Decimal(0)
            total_after_discount = sub_total - discount
            grand_total = total_after_discount
        elif invoice_data.get("invoice_type") == "TAMILNADU_CUSTOMER":
            sgst = sub_total * SGST_RATE
            cgst = sub_total * CGST_RATE
            igst = Decimal(0)
            total_after_discount = sub_total - discount
            grand_total = total_after_discount + sgst + cgst
        elif invoice_data.get("invoice_type") == "USD":
            sgst = Decimal(0)
            cgst = Decimal(0)
            igst = Decimal(0)
            total_after_discount = sub_total - discount
            grand_total = total_after_discount
        elif invoice_data.get("invoice_type") == "OTHER_STATE_CUSTOMER":
            sgst = Decimal(0)
            cgst = Decimal(0)
            igst = sub_total * IGST_RATE
            total_after_discount = sub_total - discount
            grand_total = total_after_discount + igst

    if invoice_data.get("invoice_mode") == "PERFORMA_INVOICE":
        if invoice_data.get("invoice_type") == "PERFORMA_EXEMPTED_CUSTOMER":
            sgst = Decimal(0)
            cgst = Decimal(0)
            igst = Decimal(0)
            total_after_discount = sub_total - discount
            grand_total = total_after_discount
        elif invoice_data.get("invoice_type") == "PERFORMA_TAMILNADU_CUSTOMER":
            sgst = sub_total * PERFORMA_SGST_RATE
            cgst = sub_total * PERFORMA_CGST_RATE
            igst = Decimal(0)
            total_after_discount = sub_total - discount
            grand_total = total_after_discount + sgst + cgst
        elif invoice_data.get("invoice_type") == "PERFORMA_USD":
            sgst = Decimal(0)
            cgst = Decimal(0)
            igst = Decimal(0)
            total_after_discount = sub_total - discount
            grand_total = total_after_discount
        elif invoice_data.get("invoice_type") == "PERFORMA_OTHER_STATE_CUSTOMER":
            sgst = Decimal(0)
            cgst = Decimal(0)
            igst = sub_total * IGST_RATE
            total_after_discount = sub_total - discount
            grand_total = total_after_discount + igst

    invoice_data["sgst"] = sgst.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    invoice_data["cgst"] = cgst.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    invoice_data["igst"] = igst.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    invoice_data["discount"] = discount.quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    invoice_data["sub_total"] = sub_total.quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    # invoice_data["grand_total"] = grand_total.quantize(
    #     Decimal("0.01"), rounding=ROUND_HALF_UP
    # ) 
    # invoice_data["grand_total"] = round(grand_total, 2)
    rounded_total = round(grand_total)
    invoice_data["grand_total"] = Decimal(f"{rounded_total:.2f}")
    # Generate invoice code and create invoice
    code = await Invoice.generate_next_code(db_session, invoice_data.get("invoice_mode"))
    invoice_data["invoice_code"] = code

    if invoice_data.get("invoice_type") == "USD":
        lut_arn = await Invoice.get_lut_arn(db_session)
        invoice_data["lut_arn"] = lut_arn

    invoice = Invoice(**invoice_data)
    db_session.add(invoice)
    await db_session.commit()  # Commit to generate the invoice ID

    # Now, create InvoiceTestParameter entries using the generated invoice id
    for param_data in parameters:
        param_data.update(update_dict)
        total_testing_charge = Decimal(param_data["testing_charge"]) * Decimal(
            param_data["no_of_tested"]
        )
        param_data["total_testing_charge"] = total_testing_charge

        # Create InvoiceTestParameter entry
        test_param = InvoiceTestParameter(
            **param_data,
            invoice_id=invoice.id,  # Now invoice.id is available
        )
        db_session.add(test_param)

    # Final commit to save the InvoiceTestParameter entries
    await db_session.commit()


@router.put("/{id}", status_code=204)
async def update_invoice(
    id: int, data: InvoiceUpdate, db_session: db_dep, current_user: user_dep
):
    time = datetime.now()
    update_dict = {
        "updated_at": time,
        "updated_by": current_user["id"],
    }

    # Fetch the existing invoice
    invoice = await Invoice.get_one(db_session, [Invoice.id == id])

    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Update invoice data
    invoice_data = data.model_dump()
    invoice_data.update(update_dict)
    parameters = invoice_data.pop("parameters")

    # Update invoice fields
    for key, value in invoice_data.items():
        setattr(invoice, key, value)

    # Fetch existing parameters
    existing_params = {param.id: param for param in invoice.invoice_parameters}

    # Determine parameters to delete
    updated_param_ids = {
        param_data.get("id") for param_data in parameters if param_data.get("id")
    }
    params_to_delete = [
        param
        for param_id, param in existing_params.items()
        if param_id not in updated_param_ids
    ]

    # Delete missing parameters
    for param in params_to_delete:
        await db_session.delete(param)

    # Update existing or add new parameters
    sub_total = Decimal(0)  # Start with recalculating sub_total
    for param_data in parameters:
        param_id = param_data.get("id")
        total_testing_charge = Decimal(param_data["testing_charge"]) * Decimal(
            param_data["no_of_tested"]
        )
        param_data["total_testing_charge"] = total_testing_charge
        sub_total += total_testing_charge

        if (
            param_id and param_id != ""
        ):  # Check if param_id is valid and not an empty string
            param = existing_params.get(int(param_id))
            if param:
                # Update existing parameter
                param_data.update(update_dict)
                for key, value in param_data.items():
                    setattr(param, key, value)
            else:
                raise HTTPException(
                    status_code=404, detail=f"Parameter with ID {param_id} not found"
                )
        else:
            # Create new parameter
            param_data.pop(
                "id", None
            )  # Remove 'id' if present, as it's automatically created
            param_data["created_by"] = current_user["id"]
            param_data["created_at"] = datetime.now()
            param_data.update(update_dict)
            new_param = InvoiceTestParameter(
                **param_data,
                invoice_id=invoice.id,
            )
            db_session.add(new_param)

    # Calculate SGST, CGST, discount, and grand_total based on invoice_type
    discount = Decimal(invoice_data.get("discount", 0))
    print("sub_total", sub_total)
    # Calculate totals based on invoice_type
    if invoice.invoice_mode == "INVOICE":

        if invoice_data.get("invoice_type") == "EXEMPTED_CUSTOMER":
            sgst = Decimal(0)
            cgst = Decimal(0)
            igst = Decimal(0)
            total_after_discount = sub_total - discount
            grand_total = total_after_discount
        elif invoice_data.get("invoice_type") == "TAMILNADU_CUSTOMER":
            sgst = sub_total * SGST_RATE
            cgst = sub_total * CGST_RATE
            igst = Decimal(0)
            total_after_discount = sub_total - discount
            grand_total = total_after_discount + sgst + cgst
        elif invoice_data.get("invoice_type") == "USD":
            sgst = Decimal(0)
            cgst = Decimal(0)
            igst = Decimal(0)
            total_after_discount = sub_total - discount
            grand_total = total_after_discount
        elif invoice_data.get("invoice_type") == "OTHER_STATE_CUSTOMER":
            sgst = Decimal(0)
            cgst = Decimal(0)
            igst = sub_total * IGST_RATE
            total_after_discount = sub_total - discount
            grand_total = total_after_discount + igst

    
    if invoice.invoice_mode == "PERFORMA_INVOICE":
        if invoice_data.get("invoice_type") == "PERFORMA_EXEMPTED_CUSTOMER":
            sgst = Decimal(0)
            cgst = Decimal(0)
            igst = Decimal(0)
            total_after_discount = sub_total - discount
            grand_total = total_after_discount
        elif invoice_data.get("invoice_type") == "PERFORMA_TAMILNADU_CUSTOMER":
            sgst = sub_total * PERFORMA_SGST_RATE
            cgst = sub_total * PERFORMA_CGST_RATE
            igst = Decimal(0)
            total_after_discount = sub_total - discount
            grand_total = total_after_discount + sgst + cgst
        elif invoice_data.get("invoice_type") == "PERFORMA_USD":
            sgst = Decimal(0)
            cgst = Decimal(0)
            igst = Decimal(0)
            total_after_discount = sub_total - discount
            grand_total = total_after_discount
        elif invoice_data.get("invoice_type") == "PERFORMA_OTHER_STATE_CUSTOMER":
            sgst = Decimal(0)
            cgst = Decimal(0)
            igst = sub_total * IGST_RATE
            total_after_discount = sub_total - discount
            grand_total = total_after_discount + igst

    # Update invoice with new calculated values
    invoice.sgst = sgst.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    invoice.cgst = cgst.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    invoice.igst = igst.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    invoice.discount = discount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    invoice.sub_total = sub_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    # invoice.grand_total = round(grand_total, 2)
    rounded_total = round(grand_total)
    invoice.grand_total = Decimal(f"{rounded_total:.2f}")

    # Commit all changes in a single transaction
    await db_session.commit()


@router.patch("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def patch_sample(
    invoice_id: int,
    updated_invoice: PatchInvoice,
    db_session: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user),
):

    invoice_data = updated_invoice.model_dump(exclude_unset=True)

    invoice = await Invoice.get_one(db_session, [Invoice.id == invoice_id])
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    time = datetime.now()
    update_dict = {
        "updated_at": time,
        "updated_by": current_user["id"],
    }
    # if "comment" in sample_data:
    comments = invoice_data.pop("comments", "")

    extra_data: dict[str, str] = {}

    invoice_data = {**invoice_data, **update_dict, **extra_data}

    prev_status = invoice.status
    # if "status_id" in sample_data:
    #     status_id = sample_data.pop("status_id", "")

    # await sample.update_sample(sample_data)
    # sample_data.update({"status_id": status_id})
    if invoice_data.get("status", "") == "Submitted" and prev_status != "Submitted":

        await invoice.update_invoice(invoice_data)

        await invoice.create_workflow(db_session, current_user)
        history = {
            "invoice_id": invoice_id,
            "created_at": time,
            "created_by": current_user["id"],
            "from_status_id": 1,
            "to_status_id": 2,
        }
        if invoice_data.get("assigned_to", ""):
            print("assinged_to")
            print(invoice_data.get("assigned_to", ""))
            history.update({"assigned_to": invoice_data.get("assigned_to", "")})
        if comments:
            history.update({"comments": comments})

        await invoice.create_history(db_session, current_user, history)
    else:
        if invoice_data.get("status_id", ""):
            if "status_id" in invoice_data:
                status_id = invoice_data.pop("status_id", "")

            await invoice.update_invoice(invoice_data)
            invoice_data.update({"status_id": status_id})
            progress = await InvoiceWorkflow.get_one(
                db_session,
                [
                    InvoiceWorkflow.invoice_id == invoice_id,
                    InvoiceWorkflow.status == "In Progress",
                ],
            )

            progres_status_id = progress.invoice_status_id if progress else 0
            print("progres_status_id", progres_status_id)
            if progress and invoice_data.get("status_id", "") == progres_status_id + 1:
                # moving forward
                update_dict = {
                    "status": "Done",
                    "updated_at": time,
                    "updated_by": current_user["id"],
                }
                if invoice_data.get("assigned_to", ""):
                    update_dict.update(
                        {"assigned_to": invoice_data.get("assigned_to", "")}
                    )
                print(update_dict)
                await progress.update_workflow(update_dict)

                new_status = await InvoiceWorkflow.get_one(
                    db_session,
                    [
                        InvoiceWorkflow.invoice_id == invoice_id,
                        InvoiceWorkflow.invoice_status_id == progres_status_id + 1,
                    ],
                )
                if new_status:
                    update_dict = {
                        "status": "In Progress",
                        "updated_at": time,
                        "updated_by": current_user["id"],
                    }
                    if invoice_data.get("assigned_to", ""):
                        update_dict.update(
                            {"assigned_to": invoice_data.get("assigned_to", "")}
                        )

                    await new_status.update_workflow(update_dict)

            elif (
                progress and invoice_data.get("status_id", "") == progres_status_id - 1
            ):
                print("how")
                # moving forward
                update_dict = {
                    "status": "Yet To Start",
                    "updated_at": time,
                    "updated_by": current_user["id"],
                }
                if invoice_data.get("assigned_to", ""):
                    invoice_data.update(
                        {"assigned_to": invoice_data.get("assigned_to", "")}
                    )
                await progress.update_workflow(update_dict)

                new_status = await InvoiceWorkflow.get_one(
                    db_session,
                    [
                        InvoiceWorkflow.invoice_id == invoice_id,
                        InvoiceWorkflow.invoice_status_id == progres_status_id - 1,
                    ],
                )
                if new_status:
                    update_dict = {
                        "status": "In Progress",
                        "updated_at": time,
                        "updated_by": current_user["id"],
                    }
                    if invoice_data.get("assigned_to", ""):
                        update_dict.update(
                            {"assigned_to": invoice_data.get("assigned_to", "")}
                        )
                    await new_status.update_workflow(update_dict)
            if progress:
                print(invoice_data.get("status_id", ""))
                history = {
                    "invoice_id": invoice_id,
                    "created_at": time,
                    "created_by": current_user["id"],
                    "to_status_id": invoice_data.get("status_id", ""),
                    "from_status_id": progres_status_id,
                    "comments": invoice_data.get("comments", ""),
                }
                if invoice_data.get("assigned_to", ""):
                    history.update({"assigned_to": invoice_data.get("assigned_to", "")})
                if comments:
                    history.update({"comments": comments})

                await invoice.create_history(db_session, current_user, history)
            await db_session.commit()
            # auto update sample status

            update_data = {"status_id": invoice_data.get("status_id", "")}
            await invoice.update_invoice(update_data)
    await db_session.commit()
    await db_session.refresh(invoice)


@router.delete("/{id}")
async def delete_invoice(id: int, db_session: db_dep, current_user: user_dep):

    quotation = await Invoice.get_one(db_session, [Invoice.id == id])
    if quotation is None:
        raise HTTPException(status_code=404, detail="Data not found")

    await db_session.delete(quotation)
    await db_session.commit()
