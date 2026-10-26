"""HTTP layer for the Tawseel parcel service.

The HTTP layer translates requests into calls to app.domain; the domain decides.
See README.md for the four operations, their operationIds and their errors.
"""
import base64


from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.domain import EventType, InvalidTransition, Parcel, ParcelState, apply_event  # noqa: F401


class CreateParcelBody(BaseModel):
    merchant_ref: str = Field(min_length=1, max_length=64)
    cod_amount_piastres: int = Field(ge=0, le=5_000_000)
    address_text: str = Field(min_length=1, max_length=500)


class ParcelEventBody(BaseModel):
    type: EventType


def parcel_data(parcel: Parcel) -> dict:
    return {
        "id": parcel.id,
        "merchant_ref": parcel.merchant_ref,
        "cod_amount_piastres": parcel.cod_amount_piastres,
        "address_text": parcel.address_text,
        "state": parcel.state.value,
        "attempts": parcel.attempts,
    }


def problem(status: int, title: str, **extra) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": title,
            "status": status,
            **extra,
        },
    )


def create_app() -> FastAPI:
    app = FastAPI()
    parcels = {}
    issued_cursors = {}
    next_id = 1

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ):
        errors = []
        seen_fields = set()

        for error in exc.errors():
            loc = list(error["loc"])
            field = tuple(loc)

            if field not in seen_fields:
                errors.append({
                    "loc": loc,
                    "msg": error["msg"],
                })
                seen_fields.add(field)

        return problem(422, "Validation Error", errors=errors)

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException):
        titles = {
            400: "Bad Request",
            404: "Not Found",
            409: "Conflict",
            422: "Validation Error",
        }
        extra = {}

        if exc.status_code == 422:
            extra["errors"] = [{
                "loc": [],
                "msg": str(exc.detail),
            }]
        else:
            extra["detail"] = str(exc.detail)

        return problem(
            exc.status_code,
            titles.get(exc.status_code, "Error"),
            **extra,
        )

    @app.post(
        "/v1/parcels",
        status_code=201,
        operation_id="createParcel",
        responses={409: {}, 422: {}},
    )
    def create_parcel(body: CreateParcelBody):
        nonlocal next_id

        if any(
            parcel.merchant_ref == body.merchant_ref
            for parcel in parcels.values()
        ):
            raise HTTPException(409, "merchant_ref already exists")

        parcel_id = f"pcl_{next_id}"
        next_id += 1

        parcel = Parcel(
            id=parcel_id,
            merchant_ref=body.merchant_ref,
            cod_amount_piastres=body.cod_amount_piastres,
            address_text=body.address_text,
        )
        parcels[parcel_id] = parcel

        return JSONResponse(
            status_code=201,
            headers={"Location": f"/v1/parcels/{parcel_id}"},
            content=parcel_data(parcel),
        )

    @app.get(
        "/v1/parcels/{parcel_id}",
        operation_id="getParcel",
        responses={404: {}},
    )
    def get_parcel(parcel_id: str):
        parcel = parcels.get(parcel_id)

        if parcel is None:
            raise HTTPException(404, "Parcel not found")

        return parcel_data(parcel)

    @app.get(
        "/v1/parcels",
        operation_id="listParcels",
        responses={400: {}, 422: {}},
    )
    def list_parcels(
        state: ParcelState | None = None,
        limit: int = Query(default=20, ge=1, le=100),
        cursor: str | None = None,
    ):
        start_after = None

        if cursor is not None:
            start_after = issued_cursors.get(cursor)

            if start_after is None:
                raise HTTPException(400, "Invalid cursor")

        ordered = list(parcels.values())

        if start_after is not None:
            ids = [parcel.id for parcel in ordered]
            if start_after not in ids:
                raise HTTPException(400, "Invalid cursor")
            ordered = ordered[ids.index(start_after) + 1:]

        matching = [
            parcel for parcel in ordered
            if state is None or parcel.state == state
        ]

        page = matching[:limit]
        next_cursor = None

        if len(matching) > limit and page:
            last_id = page[-1].id
            next_cursor = base64.urlsafe_b64encode(
                last_id.encode()
            ).decode()
            issued_cursors[next_cursor] = last_id

        return {
            "items": [parcel_data(parcel) for parcel in page],
            "next_cursor": next_cursor,
        }

    @app.post(
        "/v1/parcels/{parcel_id}/events",
        operation_id="recordParcelEvent",
        responses={404: {}, 409: {}, 422: {}},
    )
    def record_parcel_event(parcel_id: str, body: ParcelEventBody):
        parcel = parcels.get(parcel_id)

        if parcel is None:
            raise HTTPException(404, "Parcel not found")

        try:
            updated = apply_event(parcel, body.type)
        except InvalidTransition:
            raise HTTPException(409, "Invalid parcel state transition")

        parcels[parcel_id] = updated
        return parcel_data(updated)

    
    return app


# `uvicorn app.api:app` needs a module-level app. Once create_app() works,
# replace the line below with:  app = create_app()
app = create_app()
