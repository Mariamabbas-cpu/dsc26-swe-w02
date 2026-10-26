"""Parcel lifecycle rules for Tawseel.

Pure Python: do not import fastapi, starlette, pydantic or sqlalchemy here
(a hidden test checks). Keep the names below exactly as they are.
"""
from dataclasses import dataclass, replace
from enum import StrEnum

MAX_ATTEMPTS = 3


class ParcelState(StrEnum):
    CREATED = "created"
    OUT_FOR_DELIVERY = "out_for_delivery"
    FAILED_ATTEMPT = "failed_attempt"
    DELIVERED = "delivered"
    RETURNED = "returned"


class EventType(StrEnum):
    DISPATCH = "dispatch"
    DELIVER = "deliver"
    FAIL = "fail"
    RETURN = "return"


class InvalidTransition(Exception): ...


@dataclass(frozen=True)
class Parcel:
    id: str
    merchant_ref: str
    cod_amount_piastres: int
    address_text: str
    state: ParcelState = ParcelState.CREATED
    attempts: int = 0



def apply_event(parcel: Parcel, event: EventType) -> Parcel:
    if parcel.state == ParcelState.CREATED:
        if event == EventType.DISPATCH:
            return replace(
                parcel,
                state=ParcelState.OUT_FOR_DELIVERY,
                attempts=parcel.attempts + 1,
            )

    elif parcel.state == ParcelState.OUT_FOR_DELIVERY:
        if event == EventType.DELIVER:
            return replace(parcel, state=ParcelState.DELIVERED)

        if event == EventType.FAIL:
            return replace(parcel, state=ParcelState.FAILED_ATTEMPT)

    elif parcel.state == ParcelState.FAILED_ATTEMPT:
        if event == EventType.DISPATCH and parcel.attempts < MAX_ATTEMPTS:
            return replace(
                parcel,
                state=ParcelState.OUT_FOR_DELIVERY,
                attempts=parcel.attempts + 1,
            )

        if event == EventType.RETURN:
            return replace(parcel, state=ParcelState.RETURNED)

    raise InvalidTransition(
        f"Event '{event}' is not allowed for state '{parcel.state}'"
    )

