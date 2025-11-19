# -*- coding: utf-8 -*-
import datetime
from xml.etree import ElementTree as ET

from .models import (
    Amount,
    AnonymousPassenger,
    Booking,
    BookingEntity,
    Carrier,
    Coupon,
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
from .models import (
    AirShoppingResponse,
    OrderViewResponse,
)


def is_cancel_success(resp):
    """Checks if cancel order request was successful.

    :param resp: text of Mixvel_OrderCancelRS
    :type resp: lxml.etree._Element
    :rtype: bool
    """
    return all(
        (node.text or "") == "Success"
        for node in resp.findall(".//OperationStatus")
    )


def parse_air_shopping_response(resp):
    """Parse air shopping response.

    :param resp: text of Mixvel_AirShoppingRS
    :type resp: lxml.etree._Element
    :rtype: AirShoppingResponse
    """
    offer_elements = resp.findall("./Response/Offer")
    if not offer_elements:
        return AirShoppingResponse(offers=[], data_lists=DataLists())
    offers = [parse_offer(offer) for offer in offer_elements]
    data_lists = parse_data_lists(resp.find("./Response/DataLists"))
    return AirShoppingResponse(offers, data_lists)


def parse_order_view_response(resp):
    """Parse order view response.

    :param resp: text of Mixvel_OrderCancelRS
    :type resp: lxml.etree._Element
    :rtype: OrderViewResponse
    """
    mix_order = parse_mix_order(resp.find("./Response/MixOrder"))
    data_lists = parse_data_lists(resp.find("./Response/DataLists"))
    ticket_doc_info_nodes = resp.findall("./Response/TicketDocInfo")
    ticket_doc_info = (
        [parse_ticket_doc_info(doc) for doc in ticket_doc_info_nodes]
        if ticket_doc_info_nodes
        else None
    )

    return OrderViewResponse(mix_order, data_lists, ticket_doc_info=ticket_doc_info)


def parse_amount(elm):
    """Parses AmountType.

    :param elm: AmountType element
    :type elm: lxml.etree._Element
    :rtype: Amount
    """
    return Amount(int(elm.text.replace(".", "")), elm.get("CurCode"))


def parse_booking(elm):
    """Parses BookingType.

    :param elm: BookingType element
    :type elm: lxml.etree._Element
    :rtype: Booking
    """
    booking_id = elm.find("./BookingID").text
    entity = (
        parse_booking_entity(elm.find("./BookingEntity"))
        if elm.find("./BookingEntity") is not None
        else None
    )
    type_code = (
        elm.find("./BookingRefTypeCode").text
        if elm.find("./BookingRefTypeCode") is not None
        else None
    )
    return Booking(booking_id, entity=entity, type_code=type_code)


def parse_booking_entity(elm):
    carrier = (
        parse_carrier(elm.find("./Carrier"))
        if elm.find("./Carrier") is not None
        else None
    )
    return BookingEntity(carrier=carrier)


def parse_carrier(elm):
    airline_desig_code = (
        elm.find("./AirlineDesigCode").text
        if elm.find("./AirlineDesigCode") is not None
        else None
    )
    mixvel_airline_id = None  # TODO: implement parser
    return Carrier(
        airline_desig_code=airline_desig_code, mixvel_airline_id=mixvel_airline_id
    )


def parse_coupon(elm):
    coupon_number = float(elm.find("./CouponNumber").text)
    fare_basis_code = (
        elm.find("./FareBasisCode").text
        if elm.find("./FareBasisCode") is not None
        else None
    )
    pax_segment_ref_ids = [
        ref_id.text
        for ref_id in elm.findall("./SoldAirlineInfo/PaxSegmentRefID")
        if ref_id.text
    ]
    return Coupon(
        coupon_number,
        fare_basis_code=fare_basis_code,
        pax_segment_ref_ids=pax_segment_ref_ids,
    )


def parse_data_lists(elm):
    """Parse DataListsType.

    :param elm: DataListsType element
    :type elm: lxml.etree._Element
    :rtype: DataLists
    """
    origin_dest_list = [
        parse_origin_dest(node)
        for node in elm.findall("./OriginDestList/OriginDest")
    ]
    pax_journey_list = [
        parse_pax_journey(node)
        for node in elm.findall("./PaxJourneyList/PaxJourney")
    ]
    pax_segment_list = [
        parse_pax_segment(node)
        for node in elm.findall("./PaxSegmentList/PaxSegment")
    ]
    validating_party_list = [
        parse_validating_party(node)
        for node in elm.findall("./ValidatingPartyList/ValidatingParty")
    ]

    return DataLists(
        origin_dest_list=origin_dest_list,
        pax_journey_list=pax_journey_list,
        pax_segment_list=pax_segment_list,
        validating_party_list=validating_party_list,
    )


def parse_dated_marketing_segment(elm):
    """Parse DatedMarketingSegmentType.

    :param elm: DatedMarketingSegmentType element
    :type elm: lxml.etree._Element
    :rtype: DatedMarketingSegment
    """
    carrier_code = elm.find("./CarrierDesigCode").text
    flight_number = elm.find("./MarketingCarrierFlightNumberText").text

    return DatedMarketingSegment(carrier_code, flight_number)


def parse_fare_component(elm):
    """Parse FareComponentType.

    :param elm: FareComponentType element
    :type elm: lxml.etree._Element
    :rtype: FareComponent
    """
    fare_basis_code = elm.find("./FareBasisCode").text
    rbd = parse_rbd_avail(elm.find("./RBD"))
    price = parse_price(elm.find("./Price"))
    pax_segment_ref_id = elm.find("./PaxSegmentRefID").text

    return FareComponent(fare_basis_code, rbd, price, pax_segment_ref_id)


def parse_fare_detail(elm):
    """Parse FareDetailType.

    :param elm: FareDetailType element
    :type elm: lxml.etree._Element
    :rtype: FareDetail
    """
    fare_components = [
        parse_fare_component(fc)
        for fc in elm.findall("./FareComponent")
    ]
    pax_ref_id = elm.find("./PaxRefID").text

    return FareDetail(fare_components, pax_ref_id)


def parse_mix_order(elm):
    """Parses MixOrderType.

    :param elm: MixOrderType element
    :type elm: lxml.etree._Element
    :rtype: MixOrder
    """
    mix_order_id = elm.find("./MixOrderID").text
    orders = []
    for order_node in elm.findall("./Order"):
        orders.append(parse_order(order_node))
    total_amount = parse_amount(elm.find("./TotalAmount"))

    return MixOrder(mix_order_id, orders, total_amount)


def parse_offer(elm):
    """Parse OfferType.

    :param elm: OfferType element
    :type elm: lxml.etree._Element
    :rtype: OfferItem
    """
    offer_id = elm.find("./OfferID").text
    offer_items = [
        parse_offer_item(offer_item)
        for offer_item in elm.findall("./OfferItem")
    ]
    owner_code = elm.find("./OwnerCode").text
    timelimit = elm.find("./OfferExpirationTimeLimitDateTime").text
    timelimit = timelimit.split(".")[0].rstrip("Z")
    timelimit = datetime.datetime.strptime(timelimit, "%Y-%m-%dT%H:%M:%S")
    ticket_docs_count = (
        int(elm.find("./TicketDocsCount").text)
        if elm.find("./TicketDocsCount") is not None
        else None
    )
    total_price = (
        parse_price(elm.find("./TotalPrice"))
        if elm.find("./TotalPrice") is not None
        else None
    )

    return Offer(
        offer_id,
        offer_items,
        owner_code,
        timelimit,
        ticket_docs_count=ticket_docs_count,
        total_price=total_price,
    )


def parse_offer_item(elm):
    """Parse OfferItemType.

    :param elm: OfferItemType element
    :type elm: lxml.etree._Element
    :rtype: OfferItem
    """
    offer_item_id = elm.find("./OfferItemID").text
    price = parse_price(elm.find("./Price"))
    services = [parse_service(service) for service in elm.findall("./Service")]
    fare_details = [
        parse_fare_detail(fare_detail)
        for fare_detail in elm.findall("./FareDetail")
    ]

    return OfferItem(offer_item_id, price, services, fare_details=fare_details)


def parse_order(elm):
    """Parses OrderType.

    :param elm: OrderType element
    :type elm: lxml.etree._Element
    :rtype: Order
    """
    order_id = elm.find("./OrderID").text
    order_items = [parse_order_item(node) for node in elm.findall("./OrderItem")]
    booking_refs = [parse_booking(node) for node in elm.findall("./BookingRef")]
    total_price = parse_price(elm.find("./TotalPrice"))

    return Order(order_id, booking_refs, order_items, total_price)


def parse_order_item(elm):
    """Parses OrderItemType.

    :param elm: OrderItemType element
    :type elm: lxml.etree._Element
    :rtype: OrderItem
    """
    order_item_id = elm.find("./OrderItemID").text
    fare_details = []
    for fare_detail_node in elm.findall("./FareDetail"):
        fare_details.append(parse_fare_detail(fare_detail_node))
    price = parse_price(elm.find("./Price"))

    return OrderItem(order_item_id, fare_details, price)


def parse_origin_dest(elm):
    """Parses OriginDestType.

    :param elm: OriginDestType element
    :type elm: lxml.etree._Element
    :rtype: OriginDest
    """
    origin_code = elm.find("./OriginCode").text
    dest_code = elm.find("./DestCode").text
    origin_dest_id = (
        elm.find("./OriginDestID").text
        if elm.find("./OriginDestID") is not None
        else None
    )
    pax_journey_ref_ids = [
        ref_id.text for ref_id in elm.findall("./PaxJourneyRefID") if ref_id.text
    ]

    return OriginDest(
        origin_code,
        dest_code,
        origin_dest_id=origin_dest_id,
        pax_journey_ref_ids=pax_journey_ref_ids,
    )


def parse_pax_journey(elm):
    """Parses PaxJourneyType.

    :param elm: PaxJourneyType element
    :type elm: lxml.etree._Element
    :rtype: PaxJourney
    """
    pax_journey_id = elm.find("./PaxJourneyID").text
    pax_segment_ref_ids = [
        ref_id.text for ref_id in elm.findall("./PaxSegmentRefID") if ref_id.text
    ]

    return PaxJourney(pax_journey_id, pax_segment_ref_ids)


def parse_pax_segment(elm):
    """Parse PaxSegmentType.

    :param elm: PaxSegmentType element
    :type elm: lxml.etree._Element
    :rtype: PaxSegment
    """
    pax_segment_id = elm.find("./PaxSegmentID").text
    dep = parse_transport_dep_arrival(elm.find("./Dep"))
    arrival = parse_transport_dep_arrival(elm.find("./Arrival"))
    marketing_carrier_info = parse_dated_marketing_segment(
        elm.find("./MarketingCarrierInfo")
    )
    duration = (
        elm.find("./Duration").text if elm.find("./Duration") is not None else None
    )

    return PaxSegment(
        pax_segment_id, dep, arrival, marketing_carrier_info, duration=duration
    )


def parse_price(elm):
    """Parse PriceType.

    :param elm: PriceType element
    :type elm: lxml.etree._Element
    :rtype: Price
    """
    tax_summary = (
        parse_tax_summary(elm.find("./TaxSummary"))
        if elm.find("./TaxSummary") is not None
        else TaxSummary([])
    )
    total_amount = parse_amount(elm.find("./TotalAmount"))

    return Price(tax_summary, total_amount)


def parse_rbd_avail(elm):
    """Parse Rbd_Avail_Type.

    :param elm: Rbd_Avail_Type element
    :type elm: lxml.etree._Element
    :rtype: RbdAvail
    """
    rbd_code = elm.find("./RBD_Code").text
    availability = (
        int(elm.find("Availability").text)
        if elm.find("Availability") is not None
        else None
    )

    return RbdAvail(rbd_code, availability=availability)


def parse_service(elm):
    """Parse ServiceType.

    :param elm: ServiceType element
    :type elm: lxml.etree._Element
    :rtype: Service
    """
    service_id = elm.find("./ServiceID").text
    pax_ref_ids = [ref_id.text for ref_id in elm.findall("./PaxRefID") if ref_id.text]
    service_associations = parse_service_offer_associations(
        elm.find("./ServiceAssociations")
    )
    validating_party_ref_id = (
        elm.find("./ValidatingPartyRefID").text
        if elm.find("./ValidatingPartyRefID") is not None
        else None
    )

    return Service(
        service_id,
        pax_ref_ids,
        service_associations,
        validating_party_ref_id=validating_party_ref_id,
        validating_party_type=None,
        pax_types=None,
    )


def parse_service_offer_associations(elm):
    """Parse ServiceOfferAssociationsType.

    :param elm: ServiceOfferAssociations element
    :type elm: lxml.etree._Element
    :rtype: ServiceOfferAssociations
    """
    pax_journey_ref_ids = [
        ref_id.text
        for ref_id in elm.findall("./PaxJourneyRef/PaxJourneyRefID")
        if ref_id.text
    ]
    pax_segment_ref_ids = [
        ref_id.text
        for ref_id in elm.findall("./PaxSegmentRef/PaxSegmentRefID")
        if ref_id.text
    ]

    return ServiceOfferAssociations(
        pax_journey_ref_ids=pax_journey_ref_ids,
        pax_segment_ref_ids=pax_segment_ref_ids,
    )


def parse_tax(elm):
    """Parses TaxType.

    :param elm: TaxType element
    :type elm: lxml.etree._Element
    :rtype: Tax
    """
    return Tax(parse_amount(elm.find("./Amount")), elm.find("./TaxCode").text)


def parse_tax_summary(elm):
    """Parse TaxSummaryType.

    :param elm: TaxSummaryType element
    :type elm: lxml.etree._Element
    :rtype: TaxSummary
    """
    taxes = [parse_tax(tax) for tax in elm.findall("./Tax")]
    total_tax_amount = (
        parse_amount(elm.find("./TotalTaxAmount"))
        if elm.find("./TotalTaxAmount") is not None
        else None
    )

    return TaxSummary(taxes, total_tax_amount=total_tax_amount)


def parse_ticket(elm):
    coupons = [parse_coupon(coupon) for coupon in elm.findall("./Coupon")]
    ticket_number = elm.find("./TicketNumber").text
    return Ticket(coupons, ticket_number)


def parse_ticket_doc_info(elm):
    pax_ref_id = elm.find("./PaxRefID").text
    tickets = [parse_ticket(ticket) for ticket in elm.findall("./Ticket")]
    return TicketDocInfo(pax_ref_id, tickets)


def parse_transport_dep_arrival(elm):
    """Parse TransportDepArrivalType.

    :param elm: TransportDepArrivalType element
    :type elm: lxml.etree._Element
    :rtype: TransportDepArrival
    """
    iata_location_code = elm.find("./IATA_LocationCode").text
    scheduled_date_time = elm.find("./ScheduledDateTime").text
    scheduled_date_time = datetime.datetime.strptime(scheduled_date_time, "%Y-%m-%dT%H:%M:%S")
    return TransportDepArrival(iata_location_code, scheduled_date_time)


def parse_validating_party(elm):
    """Parse ValidatingPartyType.

    :param elm: ValidatingPartyType element
    :type elm: lxml.etree._Element
    :rtype: ValidatingParty
    """
    validating_party_id = elm.find("./ValidatingPartyID").text
    validating_party_code = elm.find("./ValidatingPartyCode").text

    return ValidatingParty(validating_party_id, validating_party_code)
