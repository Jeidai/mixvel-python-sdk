"""Minimal end-to-end example that uses the MixVel SDK Client."""
from __future__ import annotations

import datetime as dt

from mixvel.client import Client, TEST_GATEWAY
from mixvel.models import (
    AnonymousPassenger,
    IdentityDocument,
    Individual,
    Leg,
    Passenger,
    SelectedOffer,
    SelectedOfferItem,
)


def main() -> None:
    """Search for offers, create an order, and manage it."""
    client = Client(
        login="testUser.auth@mixvel.com",
        password="passWord1!",
        structure_unit_id="12036_ALPHA",
        gateway=TEST_GATEWAY,
        verify_ssl=False,  # disable when targeting trusted gateways
    )

    shopping = client.air_shopping(
        itinerary=[Leg(origin="SVO", destination="LED", departure=dt.date(2024, 6, 1))],
        paxes=[AnonymousPassenger(pax_id="PAX1", ptc="ADT")],
    )

    offer = shopping.offers[0]
    selected_offer = SelectedOffer(
        offer_ref_id=offer.offer_id,
        selected_offer_items=[
            SelectedOfferItem(
                offer_item_ref_id=offer.offer_items[0].offer_item_id,
                pax_ref_ids=["PAX1"],
            )
        ],
    )

    passengers = [
        Passenger(
            pax_id="PAX1",
            ptc="ADT",
            individual=Individual(
                given_name="JOHN",
                middle_name="",
                surname="SMITH",
                gender="M",
                birthdate=dt.date(1990, 1, 1),
            ),
            doc=IdentityDocument(
                doc_id="111111111",
                type_code="PS",
                issuing_country_code="RU",
                expiry_date=dt.date(2030, 1, 1),
            ),
            phone="+7-900-000-00-00",
            email="john@example.com",
        )
    ]

    order = client.create_order(selected_offer=selected_offer, paxes=passengers)
    mix_order_id = order.mix_order.mix_order_id

    client.retrieve_order(mix_order_id)
    client.change_order(mix_order_id=mix_order_id, amount=1)
    client.cancel_order(mix_order_id)


if __name__ == "__main__":
    main()
