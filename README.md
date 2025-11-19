# mixvel-python-sdk

The **mixvel-python-sdk** is a Python client for the MixVel API. It simplifies the process of
integrating MixVel functionality into Python-based applications.

## Capabilities

The `mixvel.client.Client` class wraps every public MixVel order-management endpoint so you can
build a complete NDC workflow in Python:

- **Authenticate** with a login, password, and structure-unit identifier; the client stores and
  reuses the bearer token for subsequent calls (`Client.__init__` / `Client.auth`).
- **Search for offers** by calling `Client.air_shopping()` with an itinerary made of `Leg` objects
  and the passengers you want to price (`AnonymousPassenger`).
- **Create orders** from a `SelectedOffer` (built from the offer/offer-items you received during
  shopping) and a list of fully described `Passenger` instances.
- **Retrieve, change, or cancel** previously created orders using `Client.retrieve_order()`,
  `Client.change_order()` (ticket issuance), and `Client.cancel_order()`.

All request and response payloads are powered by [Pydantic v2](https://docs.pydantic.dev/) models
exposed via `mixvel.models`.  The new `mixvel.xml` module turns those models into fully-formed XML
messages (and back again) using a lightweight `pydantic-xml`-style envelope/builder, so you no
longer have to juggle Jinja templates or `lxml` in your own code.

### Typed XML messages

Every outbound API call now goes through `mixvel.xml.requests.*` to build the MixVel payload.  These
classes wrap the Pydantic domain models and emit the correct namespaces, message headers, and body
structure required by the gateway.  If you need to extend a request, you can subclass the relevant
`XmlMessage` and feed it to `Client.__request()` without touching any string templates.

## Installation

Install the package directly from PyPI (or your local wheel) in the project that needs
to access MixVel:

```sh
python -m pip install mixvel
```

To work with the sources in editable mode:

```sh
python -m pip install -e .
```

To build distributable wheels or source archives run:

```sh
python -m pip install --upgrade build
python -m build
```

## Usage

### Instantiate the client

```python
from mixvel.client import Client, TEST_GATEWAY

client = Client(
    login="testUser.auth@mixvel.com",
    password="passWord1!",
    structure_unit_id="12036_ALPHA",
    gateway=TEST_GATEWAY,  # point to the production gateway when you go live
)
```

You can pass `verify_ssl=False` when pointing the client to development gateways that use
self-signed certificates.

### Search, book, and manage an order

> Need runnable code? Check out [`examples/quickstart.py`](examples/quickstart.py) for a
> complete script you can adapt for manual testing or demos.

Run the quickstart locally after supplying real credentials via environment variables:

```sh
export MIXVEL_LOGIN="your@login"
export MIXVEL_PASSWORD="yourPassword"
export MIXVEL_STRUCTURE_ID="12345_STRUCTURE"
python examples/quickstart.py
```

The script will print the MixVel order identifier you can use later in the API.

```python
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

client = Client("login", "password", "structure", gateway=TEST_GATEWAY)

# 1. Request priced offers for the desired itinerary
shopping = client.air_shopping(
    itinerary=[Leg(origin="SVO", destination="LED", departure=dt.date(2024, 6, 1))],
    paxes=[AnonymousPassenger(pax_id="PAX1", ptc="ADT")],
)

# 2. Pick one of the offers returned by MixVel
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

# 3. Describe each passenger in detail for order creation
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

# 4. Create an order and store the returned MixVel order identifier
order = client.create_order(selected_offer=selected_offer, paxes=passengers)
mix_order_id = order.mix_order.mix_order_id

# 5. Later on you can manage the order
client.retrieve_order(mix_order_id)
client.change_order(mix_order_id=mix_order_id, amount=1)  # issue tickets
client.cancel_order(mix_order_id)
```

The models returned by each API call mirror the NDC schema, so you can navigate through the
`order.data_lists` tree to inspect segments, journeys, and validating carriers, or drill into
`offer.offer_items` to surface fare and tax details for your users.

## Development

To run tests inside a Docker container, follow these steps.

Build the Docker image

```sh
docker build -t mixvel-sdk .
```

Run the container, supplying your MixVel credentials as environment variables

```sh
docker run -t \
  -e MIXVEL_LOGIN="testUser.auth@mixvel.com" \
  -e MIXVEL_PASSWORD="passWord1!" \
  -e MIXVEL_STRUCTURE_ID="12036_ALPHA" \
  mixvel-sdk
```

Note:

- The integration tests require valid values for `MIXVEL_LOGIN`, `MIXVEL_PASSWORD`,
  and `MIXVEL_STRUCTURE_ID`.
- To obtain these credentials, please contact MixVel support at [support@mixvel.com](mailto:support@mixvel.com).
