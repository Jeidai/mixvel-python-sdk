from __future__ import annotations

import datetime as _dt
from mixvel._compat.pydantic import BaseModel, ConfigDict, Field


class MixvelModel(BaseModel):
    """Base class for all domain models with sensible defaults."""

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)


class Amount(MixvelModel):
    amount: int
    cur_code: str | None = None


class AnonymousPassenger(MixvelModel):
    pax_id: str
    ptc: str


class BookingEntity(MixvelModel):
    carrier: "Carrier | None" = None


class Carrier(MixvelModel):
    airline_desig_code: str | None = None
    mixvel_airline_id: str | None = None


class Booking(MixvelModel):
    booking_id: str
    booking_entity: BookingEntity | None = None
    booking_ref_type_code: str | None = None


class Coupon(MixvelModel):
    coupon_number: float
    fare_basis_code: str | None = None
    pax_segment_ref_ids: list[str] | None = None


class DatedMarketingSegment(MixvelModel):
    carrier_desig_code: str
    marketing_carrier_flight_number_text: str


class TransportDepArrival(MixvelModel):
    iata_location_code: str
    scheduled_date_time: _dt.datetime


class PaxSegment(MixvelModel):
    pax_segment_id: str
    dep: TransportDepArrival
    arrival: TransportDepArrival
    marketing_carrier_info: DatedMarketingSegment
    duration: str | None = None


class PaxJourney(MixvelModel):
    pax_journey_id: str
    pax_segment_ref_ids: list[str]


class OriginDest(MixvelModel):
    origin_code: str
    dest_code: str
    origin_dest_id: str | None = None
    pax_journey_ref_ids: list[str] | None = None


class ValidatingParty(MixvelModel):
    validating_party_id: str
    validating_party_code: str


class DataLists(MixvelModel):
    origin_dest_list: list[OriginDest] = Field(default_factory=list)
    pax_journey_list: list[PaxJourney] = Field(default_factory=list)
    pax_segment_list: list[PaxSegment] = Field(default_factory=list)
    validating_party_list: list[ValidatingParty] = Field(default_factory=list)


class RbdAvail(MixvelModel):
    rbd_code: str
    availability: int | None = None


class FareComponent(MixvelModel):
    fare_basis_code: str
    rbd: RbdAvail
    price: "Price"
    pax_segment_ref_id: str


class FareDetail(MixvelModel):
    fare_components: list[FareComponent]
    pax_ref_id: str


class Tax(MixvelModel):
    amount: Amount
    tax_code: str


class TaxSummary(MixvelModel):
    taxes: list[Tax] = Field(default_factory=list)
    total_tax_amount: Amount | None = None


class Price(MixvelModel):
    tax_summary: TaxSummary | None = None
    total_amount: Amount


class ServiceOfferAssociations(MixvelModel):
    pax_journey_ref_ids: list[str] | None = None
    pax_segment_ref_ids: list[str] | None = None


class Service(MixvelModel):
    service_id: str
    pax_ref_ids: list[str]
    service_associations: ServiceOfferAssociations
    validating_party_ref_id: str | None = None
    validating_party_type: ValidatingParty | None = None
    pax_types: list[AnonymousPassenger] | None = None


class OfferItem(MixvelModel):
    offer_item_id: str
    price: Price
    services: list[Service]
    fare_details: list[FareDetail] | None = None


class Offer(MixvelModel):
    offer_id: str
    offer_items: list[OfferItem]
    owner_code: str
    offer_expiration_timelimit_datetime: _dt.datetime
    ticket_docs_count: int | None = None
    total_price: Price | None = None


class OrderItem(MixvelModel):
    order_item_id: str
    fare_details: list[FareDetail]
    price: Price


class Order(MixvelModel):
    order_id: str
    booking_refs: list[Booking]
    order_items: list[OrderItem]
    total_price: Price


class MixOrder(MixvelModel):
    mix_order_id: str
    orders: list[Order]
    total_amount: Amount


class Ticket(MixvelModel):
    coupons: list[Coupon]
    ticket_number: str


class TicketDocInfo(MixvelModel):
    pax_ref_id: str
    tickets: list[Ticket]


class Individual(MixvelModel):
    given_name: str
    middle_name: str | None = None
    surname: str
    gender: str
    birthdate: _dt.date


class IdentityDocument(MixvelModel):
    doc_id: str
    type_code: str
    issuing_country_code: str
    expiry_date: _dt.date


class Passenger(AnonymousPassenger):
    individual: Individual
    doc: IdentityDocument
    phone: str | None = None
    email: str | None = None


class SelectedOfferItem(MixvelModel):
    offer_item_ref_id: str
    pax_ref_ids: list[str]


class SelectedOffer(MixvelModel):
    offer_ref_id: str
    selected_offer_items: list[SelectedOfferItem]


class Leg(MixvelModel):
    origin: str
    destination: str
    departure: _dt.date
    cabin: str = "Economy"


class OrderViewResponse(MixvelModel):
    mix_order: MixOrder
    data_lists: DataLists
    ticket_doc_info: list[TicketDocInfo] | None = None


class AirShoppingResponse(MixvelModel):
    offers: list[Offer] = Field(default_factory=list)
    data_lists: DataLists = Field(default_factory=DataLists)
