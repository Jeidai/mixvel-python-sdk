from __future__ import annotations

from typing import List
from xml.etree import ElementTree as ET

from mixvel.models import (
    AnonymousPassenger,
    Leg,
    Passenger,
    SelectedOffer,
)

from .base import XmlMessage
from .helpers import append_text_element


class AuthRequest(XmlMessage):
    XML_TAG = "a:Auth"
    XML_NS_MAP = {"a": "https://www.mixvel.com/API/XSD/mixvel_auth/1_01"}

    login: str
    password: str
    structure_unit_id: str

    def _build_body(self, element: ET.Element) -> None:
        append_text_element(element, "Login", self.login)
        append_text_element(element, "Password", self.password)
        append_text_element(element, "StructureUnitID", self.structure_unit_id)


class AirShoppingRequest(XmlMessage):
    XML_TAG = "shop:Mixvel_AirShoppingRQ"
    XML_NS_MAP = {
        "shop": "https://www.mixvel.com/API/XSD/Mixvel_AirShoppingRQ/1_01",
    }

    itinerary: List[Leg]
    paxes: List[AnonymousPassenger]

    def _build_body(self, element: ET.Element) -> None:
        request = ET.SubElement(element, "Request")
        flight_request = ET.SubElement(request, "FlightRequest")
        od_container = ET.SubElement(flight_request, "FlightRequestOriginDestinationsCriteria")
        for leg in self.itinerary:
            od = ET.SubElement(od_container, "OriginDestCriteria")
            cabin = ET.SubElement(od, "CabinType")
            append_text_element(cabin, "CabinTypeCode", leg.cabin)
            pref = ET.SubElement(cabin, "PrefLevel")
            append_text_element(pref, "PrefLevelCode", "Required")
            dest = ET.SubElement(od, "DestArrivalCriteria")
            append_text_element(dest, "IATA_LocationCode", leg.destination)
            origin_dep = ET.SubElement(od, "OriginDepCriteria")
            append_text_element(origin_dep, "Date", leg.departure)
            append_text_element(origin_dep, "IATA_LocationCode", leg.origin)
        paxs_container = ET.SubElement(request, "Paxs")
        for pax in self.paxes:
            pax_node = ET.SubElement(paxs_container, "Pax")
            append_text_element(pax_node, "PaxID", pax.pax_id)
            append_text_element(pax_node, "PTC", pax.ptc)
        shopping = ET.SubElement(request, "ShoppingCriteria")
        pricing = ET.SubElement(shopping, "PricingMethodCriteria")
        append_text_element(pricing, "BestPricingOptionText", "Extended")
        append_text_element(pricing, "CarrierMixInd", True)


class OrderCreateRequest(XmlMessage):
    XML_TAG = "m:Mixvel_OrderCreateRQ"
    XML_NS_MAP = {"m": "https://www.mixvel.com/API/XSD/Mixvel_OrderCreateRQ/1_01"}

    selected_offer: SelectedOffer
    paxes: List[Passenger]

    def _build_body(self, element: ET.Element) -> None:
        request = ET.SubElement(element, "Request")
        create_order = ET.SubElement(request, "CreateOrder")
        offer_node = ET.SubElement(create_order, "SelectedOffer")
        append_text_element(offer_node, "OfferRefID", self.selected_offer.offer_ref_id)
        for item in self.selected_offer.selected_offer_items:
            sel_item = ET.SubElement(offer_node, "SelectedOfferItem")
            append_text_element(sel_item, "OfferItemRefID", item.offer_item_ref_id)
            for pax_ref in item.pax_ref_ids:
                append_text_element(sel_item, "PaxRefID", pax_ref)
        data_lists = ET.SubElement(request, "DataLists")
        contact_list = ET.SubElement(data_lists, "ContactInfoList")
        pax_list = ET.SubElement(data_lists, "PaxList")
        for index, pax in enumerate(self.paxes, start=1):
            contact_id = None
            if pax.email or pax.phone:
                contact = ET.SubElement(contact_list, "ContactInfo")
                contact_id = f"Contact-{index}"
                append_text_element(contact, "ContactInfoID", contact_id)
                if pax.email:
                    email = ET.SubElement(contact, "EmailAddress")
                    append_text_element(email, "ContactTypeText", "personal")
                    append_text_element(email, "EmailAddressText", pax.email)
                if pax.phone:
                    phone = ET.SubElement(contact, "Phone")
                    append_text_element(phone, "ContactTypeText", "personal")
                    append_text_element(phone, "PhoneNumber", pax.phone)
            pax_node = ET.SubElement(pax_list, "Pax")
            if contact_id:
                append_text_element(pax_node, "ContactInfoRefID", contact_id)
            doc = ET.SubElement(pax_node, "IdentityDoc")
            append_text_element(doc, "ExpiryDate", pax.doc.expiry_date)
            append_text_element(doc, "IdentityDocID", pax.doc.doc_id)
            append_text_element(doc, "IdentityDocTypeCode", pax.doc.type_code)
            append_text_element(doc, "IssuingCountryCode", pax.doc.issuing_country_code)
            append_text_element(doc, "Surname", pax.individual.surname)
            individual = ET.SubElement(pax_node, "Individual")
            append_text_element(individual, "Birthdate", pax.individual.birthdate)
            append_text_element(individual, "GenderCode", pax.individual.gender)
            append_text_element(individual, "GivenName", pax.individual.given_name)
            if pax.individual.middle_name:
                append_text_element(individual, "MiddleName", pax.individual.middle_name)
            append_text_element(individual, "Surname", pax.individual.surname)
            append_text_element(pax_node, "PaxID", pax.pax_id)
            append_text_element(pax_node, "PTC", pax.ptc)


class OrderRetrieveRequest(XmlMessage):
    XML_TAG = "o:Mixvel_OrderRetrieveRQ"
    XML_NS_MAP = {"o": "https://www.mixvel.com/API/XSD/Mixvel_OrderRetrieveRQ/1_00"}

    mix_order_id: str

    def _build_body(self, element: ET.Element) -> None:
        request = ET.SubElement(element, "Request")
        filter_criteria = ET.SubElement(request, "OrderFilterCriteria")
        mix_order = ET.SubElement(filter_criteria, "MixOrder")
        append_text_element(mix_order, "MixOrderID", self.mix_order_id)


class OrderChangeRequest(XmlMessage):
    XML_TAG = "o:Mixvel_OrderChangeRQ"
    XML_NS_MAP = {"o": "https://www.mixvel.com/API/XSD/Mixvel_OrderChangeRQ/1_00"}

    mix_order_id: str
    amount: int
    currency: str = "RUB"

    def _build_body(self, element: ET.Element) -> None:
        request = ET.SubElement(element, "Request")
        mix_order = ET.SubElement(request, "MixOrder")
        append_text_element(mix_order, "MixOrderID", self.mix_order_id)
        payment_functions = ET.SubElement(request, "PaymentFunctions")
        processing = ET.SubElement(payment_functions, "PaymentProcessingDetails")
        amount = ET.SubElement(processing, "Amount")
        amount.set("CurCode", self.currency)
        amount.text = str(self.amount)
        method = ET.SubElement(processing, "PaymentProcessingDetailsPaymentMethod")
        ET.SubElement(method, "OtherPaymentMethod")


class OrderCancelRequest(XmlMessage):
    XML_TAG = "m:Mixvel_OrderCancelRQ"
    XML_NS_MAP = {"m": "https://www.mixvel.com/API/XSD/Mixvel_OrderCancelRQ/1_01"}

    mix_order_id: str

    def _build_body(self, element: ET.Element) -> None:
        request = ET.SubElement(element, "Request")
        mix_order = ET.SubElement(request, "MixOrder")
        append_text_element(mix_order, "MixOrderID", self.mix_order_id)
