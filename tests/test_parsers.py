# -*- coding: utf-8 -*-
import datetime

from .utils import parse_xml, parse_xml_response
from mixvel._parsers import (
    is_cancel_success,
    parse_air_shopping_response,
    parse_order_view_response,
)
from mixvel._parsers import (
    parse_amount,
    parse_booking,
    parse_data_lists,
    parse_dated_marketing_segment,
    parse_fare_component,
    parse_fare_detail,
    parse_mix_order,
    parse_offer,
    parse_offer_item,
    parse_order_item,
    parse_order,
    parse_origin_dest,
    parse_pax_journey,
    parse_pax_segment,
    parse_price,
    parse_rbd_avail,
    parse_service,
    parse_service_offer_associations,
    parse_tax,
    parse_tax_summary,
    parse_ticket_doc_info,
    parse_transport_dep_arrival,
    parse_validating_party,
)
from mixvel.models import (
    AirShoppingResponse,
    OrderViewResponse,
)
from mixvel.models import (
    Amount,
    Booking,
    BookingEntity,
    Carrier,
    DataLists,
    DatedMarketingSegment,
    FareComponent,
    FareDetail,
    MixOrder,
    Offer,
    OfferItem,
    Order,
    OrderItem,
    OriginDest,
    PaxJourney,
    PaxSegment,
    Price,
    RbdAvail,
    Service,
    ServiceOfferAssociations,
    Tax,
    TaxSummary,
    Ticket,
    TicketDocInfo,
    TransportDepArrival,
    ValidatingParty,
)

import pytest


class TestParsers:
    @pytest.mark.parametrize(
        "resp_path",
        [
            "responses/order/cancel_success.xml",
        ],
    )
    def test_is_cancel_success(self, resp_path):
        resp = parse_xml_response(resp_path)
        assert is_cancel_success(resp)

    def test_parse_air_shopping_response_no_offers(self):
        resp_path = "responses/order/air-shopping__no-offers.xml"
        resp = parse_xml_response(resp_path)
        got = parse_air_shopping_response(resp)
        assert isinstance(got, AirShoppingResponse)
        assert len(got.offers) == 0

    @pytest.mark.parametrize(
        "resp_path",
        [
            "responses/order/air-shopping__RT-2ADT1CNN.xml",
            "responses/order/air-shopping__with-stop.xml",
        ],
    )
    def test_parse_air_shopping_response(self, resp_path):
        resp = parse_xml_response(resp_path)
        got = parse_air_shopping_response(resp)
        assert isinstance(got, AirShoppingResponse)
        assert isinstance(got.offers[0], Offer)
        assert isinstance(got.data_lists, DataLists)

    @pytest.mark.parametrize(
        "resp_path",
        [
            "responses/order/view.xml",
        ],
    )
    def test_parse_order_view_response(self, resp_path):
        resp = parse_xml_response(resp_path)
        got = parse_order_view_response(resp)
        assert isinstance(got, OrderViewResponse)
        assert isinstance(got.mix_order, MixOrder)
        assert isinstance(got.data_lists, DataLists)


class TestTypeParsers:
    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/amount_1.xml",
                Amount(653800, "RUB"),
            ),
            (
                "models/amount_2.xml",
                Amount(326900, "RUB"),
            ),
        ],
    )
    def test_parse_amount(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_amount(elm)
        assert got.amount == want.amount
        assert got.cur_code == want.cur_code

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/booking.xml",
                Booking("MMKW90", type_code="PNR", entity=BookingEntity()),
            ),
        ],
    )
    def test_parse_booking(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_booking(elm)
        assert got.booking_id == want.booking_id
        assert got.booking_ref_type_code == want.booking_ref_type_code
        if want.booking_entity is None:
            assert got.booking_entity is None
        else:
            assert got.booking_entity is not None

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/data-lists.xml",
                DataLists(),
            ),
        ],
    )
    def test_parse_data_lists(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_data_lists(elm)
        assert isinstance(got.origin_dest_list[0], OriginDest)
        assert isinstance(got.pax_journey_list[0], PaxJourney)
        assert isinstance(got.pax_segment_list[0], PaxSegment)
        assert isinstance(got.validating_party_list[0], ValidatingParty)

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/dated_marketing_segment.xml",
                DatedMarketingSegment(
                    "DP",  # carrier_desig_code
                    "313",  # marketing_carrier_flight_number_text
                ),
            ),
        ],
    )
    def test_parse_dated_marketing_segment(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_dated_marketing_segment(elm)
        got.carrier_desig_code == want.carrier_desig_code
        got.marketing_carrier_flight_number_text == want.marketing_carrier_flight_number_text

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/fare_component.xml",
                FareComponent(
                    "RPROWRF",  # fare_basis_code
                    RbdAvail("A"),  # rbd
                    Price(TaxSummary([]), Amount(326900, "RUB")),  # price
                    "2b8e572b-f9d5-4045-8986-1ddd88f2bb66",  # pax_segment_ref_id
                ),
            ),
        ],
    )
    def test_parse_fare_componentl(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_fare_component(elm)
        assert got.fare_basis_code == want.fare_basis_code
        assert isinstance(got.rbd, RbdAvail)
        assert isinstance(got.price, Price)
        assert got.pax_segment_ref_id == want.pax_segment_ref_id

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/fare_detail.xml",
                FareDetail([], "Pax-1"),
            ),
        ],
    )
    def test_parse_fare_detail(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_fare_detail(elm)
        assert isinstance(got.fare_components[0], FareComponent)
        assert got.pax_ref_id == want.pax_ref_id

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/mix-order.xml",
                MixOrder("01138-250530-MHY6279", [], Amount(486300, "RUB")),
            ),
        ],
    )
    def test_parse_mix_order(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_mix_order(elm)
        assert got.mix_order_id == want.mix_order_id
        assert isinstance(got.orders[0], Order)
        assert isinstance(got.total_amount, Amount)

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/offer.xml",
                Offer(
                    "63ac5143-927c-4b21-8ba5-41061fa5b2c3",  # offer_id
                    [],  # offer_items
                    "TCH",  # owner_code
                    datetime.datetime(2022, 11, 8, 19, 35, 0),  # timelimit
                    ticket_docs_count=None,
                    total_price=Price(TaxSummary([]), Amount(2024400, "RUB")),
                ),
            ),
        ],
    )
    def test_parse_offer(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_offer(elm)
        assert got.offer_id == want.offer_id
        assert isinstance(got.offer_items[0], OfferItem)
        assert got.owner_code == want.owner_code
        assert (
            got.offer_expiration_timelimit_datetime
            == want.offer_expiration_timelimit_datetime
        )
        assert got.ticket_docs_count == want.ticket_docs_count
        assert (
            got.total_price.total_amount.amount == want.total_price.total_amount.amount
        )

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/offer_item.xml",
                OfferItem(
                    "ca280e53-1dd1-4d7b-9b57-d1a45b364f29",  # offer_item_id
                    Price(TaxSummary([]), Amount(332400, "RUB")),  # price
                    [],  # services
                    fare_details=[],  # fare_details
                ),
            ),
        ],
    )
    def test_parse_offer_item(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_offer_item(elm)
        assert got.offer_item_id == want.offer_item_id
        assert isinstance(got.price, Price)
        assert isinstance(got.services[0], Service)
        assert isinstance(got.fare_details[0], FareDetail)

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/order.xml",
                Order(
                    "01138-250530-OHY6280",
                    [],  # booking_refs
                    [],  # order_items
                    Price(TaxSummary([]), Amount(486300, "RUB")),
                ),
            ),
        ],
    )
    def test_parse_order(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_order(elm)
        assert got.order_id == want.order_id
        assert isinstance(got.booking_refs[0], Booking)
        assert isinstance(got.order_items[0], OrderItem)
        assert isinstance(got.total_price, Price)

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/order_item.xml",
                OrderItem(
                    "fa21bac3-6a8c-4066-8477-148bc5f63a31",
                    [],
                    Price(TaxSummary([]), Amount(653800, "RUB")),
                ),
            ),
        ],
    )
    def test_parse_order_item(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_order_item(elm)
        assert got.order_item_id == want.order_item_id
        assert isinstance(got.fare_details[0], FareDetail)
        assert isinstance(got.price, Price)

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/origin_dest.xml",
                OriginDest(
                    "AER",  # origin_code
                    "LED",  # dest_code
                    origin_dest_id="1bf06365-48f6-466e-a971-8a3b2a232928",
                    pax_journey_ref_ids=[
                        "9f79533d-8366-42b5-8fbe-87a5e249cfce",
                        "ca76d826-725d-4ae0-a606-053b8a40b5c4",
                        "94be4cd4-c9b0-42d2-be5b-9775830c668f",
                    ],
                ),
            ),
        ],
    )
    def test_parse_origin_dest(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_origin_dest(elm)
        assert got.origin_code == want.origin_code
        assert got.dest_code == want.dest_code
        assert got.origin_dest_id == want.origin_dest_id
        assert len(got.pax_journey_ref_ids) == len(want.pax_journey_ref_ids)
        for i in range(len(got.pax_journey_ref_ids)):
            assert got.pax_journey_ref_ids[i] == want.pax_journey_ref_ids[i]

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/pax_journey.xml",
                PaxJourney(
                    "0248fd86-53a1-4eb7-aedb-acb09ad7f38e",  # pax_journey_id
                    [
                        "fafd5965-b743-4494-b72b-614c580fc502",
                    ],  # pax_segment_ref_ids
                ),
            ),
            (
                "models/pax_journey__with_stop.xml",
                PaxJourney(
                    "a973b729-ba9c-40c6-ac0c-cfb63eca682b",  # pax_journey_id
                    [
                        "a73524fe-e42b-406d-b114-a60745c5a8bf",
                        "6891d922-b662-4f0b-bbe1-7035c74dec67",
                    ],  # pax_segment_ref_ids
                ),
            ),
        ],
    )
    def test_parse_pax_journey(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_pax_journey(elm)
        assert got.pax_journey_id == want.pax_journey_id
        assert len(got.pax_segment_ref_ids) == len(want.pax_segment_ref_ids)
        for i in range(len(got.pax_segment_ref_ids)):
            assert got.pax_segment_ref_ids[i] == want.pax_segment_ref_ids[i]

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/pax-segment.xml",
                PaxSegment(
                    "f6669d6f-9172-4f6c-9a4c-4c765f332136",
                    TransportDepArrival(
                        "OVB",
                        datetime.datetime(2025, 6, 13, 10, 5, 0),
                    ),
                    TransportDepArrival(
                        "SVO",
                        datetime.datetime(2025, 6, 13, 10, 30, 0),
                    ),
                    DatedMarketingSegment("SU", "1307"),
                    duration="PT4H25M",
                ),
            ),
        ],
    )
    def test_parse_pax_segment(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_pax_segment(elm)
        assert got.pax_segment_id == want.pax_segment_id
        assert isinstance(got.dep, TransportDepArrival)
        assert isinstance(got.arrival, TransportDepArrival)
        assert isinstance(got.marketing_carrier_info, DatedMarketingSegment)
        assert got.duration == want.duration

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/price.xml",
                Price(TaxSummary([]), Amount(326900, "RUB")),
            ),
        ],
    )
    def test_parse_price(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_price(elm)
        assert isinstance(got.tax_summary, TaxSummary)
        assert got.total_amount.amount == want.total_amount.amount

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/rbd_avail.xml",
                RbdAvail("A", availability=9),
            ),
        ],
    )
    def test_parse_rbd_avail(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_rbd_avail(elm)
        assert got.rbd_code == want.rbd_code
        assert got.availability == want.availability

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/service.xml",
                Service(
                    "fd45bc97-0e26-48bd-aa2a-7c49672e604a",  # service_id
                    ["Pax-1", "Pax-2"],  # pax_ref_ids
                    ServiceOfferAssociations(),  # service_associations
                    validating_party_ref_id="7036ae6a-a67e-4986-a6f6-60465a7beadc",
                ),
            ),
        ],
    )
    def test_parse_service(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_service(elm)
        assert got.service_id == want.service_id
        assert len(got.pax_ref_ids) == len(want.pax_ref_ids)
        for i in range(len(want.pax_ref_ids)):
            got.pax_ref_ids[i] == want.pax_ref_ids[i]
        assert isinstance(got.service_associations, ServiceOfferAssociations)
        assert got.validating_party_ref_id == want.validating_party_ref_id

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/service_offer_associations.xml",
                ServiceOfferAssociations(
                    pax_journey_ref_ids=[
                        "94be4cd4-c9b0-42d2-be5b-9775830c668f",
                        "54728d42-73b5-42e9-8fb5-4b7982e294d0",
                    ],
                    pax_segment_ref_ids=None,
                ),
            ),
            (
                "models/service_offer_associations_with_segment_ref.xml",
                ServiceOfferAssociations(
                    pax_journey_ref_ids=None,
                    pax_segment_ref_ids=[
                        "9222bf7d-79e0-481a-b832-2ea0dac317f0",
                    ],
                ),
            ),
        ],
    )
    def test_parse_service_offer_associations(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_service_offer_associations(elm)
        if want.pax_journey_ref_ids:
            assert len(want.pax_journey_ref_ids) == len(got.pax_journey_ref_ids)
            for i in range(len(want.pax_journey_ref_ids)):
                got.pax_journey_ref_ids[i] == want.pax_journey_ref_ids[i]
        if want.pax_segment_ref_ids:
            assert len(want.pax_segment_ref_ids) == len(got.pax_segment_ref_ids)
            for i in range(len(want.pax_segment_ref_ids)):
                got.pax_segment_ref_ids[i] == want.pax_segment_ref_ids[i]

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/tax__zero_amount.xml",
                Tax(Amount(0, None), "ZZ"),
            ),
        ],
    )
    def test_parse_tax(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_tax(elm)
        assert got.amount.amount == want.amount.amount
        assert got.amount.cur_code == want.amount.cur_code
        assert got.tax_code == want.tax_code

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/tax_summary.xml",
                TaxSummary([], Amount(68400, "RUB")),
            ),
            (
                "models/tax_summary__null_total_tax_amount.xml",
                TaxSummary([], None),
            ),
        ],
    )
    def test_parse_tax(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_tax_summary(elm)
        assert isinstance(got.taxes[0], Tax)
        if want.total_tax_amount is not None:
            assert got.total_tax_amount.amount == want.total_tax_amount.amount
        else:
            assert got.total_tax_amount is None

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/ticket-doc-info.xml",
                TicketDocInfo(
                    "Pax-3",
                    [
                        Ticket([], "7706102021825"),
                    ],
                ),
            ),
        ],
    )
    def test_parse_ticket_doc_info(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_ticket_doc_info(elm)
        assert got.pax_ref_id == want.pax_ref_id
        assert len(got.tickets) == len(want.tickets)

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/transport-dep-arrival.xml",
                TransportDepArrival(
                    "SVO",
                    datetime.datetime(
                        2025, 6, 13, 19, 30, 0
                    ),
                ),
            ),
            (
                "models/transport-dep-arrival__null-terminal.xml",
                TransportDepArrival(
                    "KVX",
                    datetime.datetime(
                        2025, 6, 13, 21, 5, 0
                    ),
                ),
            ),
        ],
    )
    def test_parse_transport_dep_arrival(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_transport_dep_arrival(elm)
        assert got.iata_location_code == want.iata_location_code
        assert got.scheduled_date_time == want.scheduled_date_time

    @pytest.mark.parametrize(
        "model_path,want",
        [
            (
                "models/validating_party__DP.xml",
                ValidatingParty("7036ae6a-a67e-4986-a6f6-60465a7beadc", "DP"),
            ),
        ],
    )
    def test_parse_validating_party(self, model_path, want):
        elm = parse_xml(model_path)
        got = parse_validating_party(elm)
        assert got.validating_party_id == want.validating_party_id
        assert got.validating_party_code == want.validating_party_code
