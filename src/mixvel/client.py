# -*- coding: utf-8 -*-
import datetime
import logging
import uuid
from xml.etree import ElementTree as ET

import httpx

from mixvel._parsers import (
    is_cancel_success,
    parse_air_shopping_response,
    parse_order_view_response,
)
from mixvel.models import (
    Passenger,
    SelectedOffer,
)
from mixvel.models import AirShoppingResponse
from mixvel.xml.base import XmlMessage
from mixvel.xml.envelope import MessageEnvelope, MessageInfo
from mixvel.xml.requests import (
    AirShoppingRequest,
    AuthRequest,
    OrderCancelRequest,
    OrderChangeRequest,
    OrderCreateRequest,
    OrderRetrieveRequest,
)

from .endpoint import is_login_endpoint
from .exceptions import NoOrdersToCancel
from .utils import strip_namespaces

PROD_GATEWAY = "https://api.mixvel.com"
TEST_GATEWAY = "https://api-test.mixvel.com"

log = logging.getLogger(__name__)
class Client:
    def __init__(
        self, login, password, structure_unit_id, gateway=PROD_GATEWAY, verify_ssl=True
    ):
        """MixVel API Client.

        :param gateway: (optional) gateway url, default is `PROD_GATEWAY`
        :type gateway: str
        :param verify_ssl: (optional) controls whether we verify the server's SSL certificate, defaults to True
        :type verify_ssl: bool
        """
        self.login = login
        self.password = password
        self.structure_unit_id = structure_unit_id
        self.token = ""
        self.gateway = gateway
        self.verify_ssl = verify_ssl
        self._client = httpx.Client(base_url=gateway, verify=verify_ssl)

    def __prepare_request(self, payload: XmlMessage) -> str:
        """Wrap the request payload in a MixVel envelope."""

        envelope = MessageEnvelope(
            message_info=MessageInfo(
                message_id=str(uuid.uuid4()),
                time_sent=datetime.datetime.utcnow().replace(
                    tzinfo=datetime.timezone.utc
                ),
            ),
            payload=payload,
        )
        return envelope.to_xml()

    def __request(self, endpoint, payload: XmlMessage):
        """Constructs and executes request.

        :param endpoint: method endpoint, e.g. "/api/Accounts/login"
        :type endpoint: str
        :param context: request variables.
        :type context: dict
        :return: content of response `Body` node.
        :rtype: lxml.etree._Element
        """
        headers = {
            "Content-Type": "application/xml",
        }
        if not is_login_endpoint(endpoint):
            if not self.token:
                self.auth()
            headers["Authorization"] = "Bearer {token}".format(token=self.token)
        data = self.__prepare_request(payload)
        self.sent = data
        log.info("%s%s", self.gateway, endpoint)
        log.info(self.sent)
        self.recv = None
        r = self._client.post(endpoint, content=data, headers=headers)
        self.recv = r.content
        log.info(self.recv)
        r.raise_for_status()
        resp = ET.fromstring(self.recv)
        strip_namespaces(resp)
        err = resp.find(".//Error")
        if err is not None:
            typ = err.find("./ErrorType").text
            code = err.find("./Code").text if err.find("./Code") is not None else ""
            desc = (
                err.find("./DescText").text.encode("utf-8")
                if err.find("./DescText") is not None
                else ""
            )
            if code == "MIX-106001":
                raise NoOrdersToCancel
            if code == "":
                code = "UNDEFINED"
            raise IOError(
                "{code}: {type}: {desc}".format(code=code, type=typ, desc=desc)
            )
        return resp.find(".//Body/AppData/")

    def auth(self):
        """Logins to MixVel API.

        :return: auth token
        :rtype: str
        """
        payload = AuthRequest(
            login=self.login,
            password=self.password,
            structure_unit_id=self.structure_unit_id,
        )
        resp = self.__request("/api/Accounts/login", payload)
        token = resp.find("./Token").text
        self.token = token

        return token

    def air_shopping(self, itinerary, paxes):
        """Executes air shopping request.

        :param itinerary: itinerary
        :type itinerary: list[Leg]
        :param paxes: paxes
        :type paxes: list[AnonymousPassenger]
        :rtype: AirShoppingResponse
        """
        payload = AirShoppingRequest(itinerary=itinerary, paxes=paxes)
        resp = self.__request("/api/Order/AirShopping", payload)
        return parse_air_shopping_response(resp)

    def create_order(self, selected_offer, paxes):
        """Creates order.

        :param selected_offer: selected offer
        :type selected_offer: SelectedOffer
        :param paxes: passengers
        :type paxes: list[Passenger]
        :rtype: OrderViewResponse
        """
        payload = OrderCreateRequest(selected_offer=selected_offer, paxes=paxes)
        resp = self.__request("/api/Order/Create", payload)
        return parse_order_view_response(resp)

    def retrieve_order(self, mix_order_id):
        """Retrieves order.

        :param mix_order_id: aggregated order id
        :type mix_order_id: str
        :rtype: OrderViewResponse
        """
        payload = OrderRetrieveRequest(mix_order_id=mix_order_id)
        resp = self.__request("/api/Order/Retrieve", payload)

        return parse_order_view_response(resp)

    def change_order(self, mix_order_id, amount):
        """Issues tickets.

        :param mix_order_id: aggregated order id
        :type mix_order_id: str
        :param amount: amount
        :type amount: int
        """
        payload = OrderChangeRequest(mix_order_id=mix_order_id, amount=amount)
        resp = self.__request("/api/Order/Change", payload)

        return parse_order_view_response(resp)

    def cancel_order(self, mix_order_id):
        """Cancels order.

        :param mix_order_id: order id
        :type mix_order_id: str
        :rtype: bool
        """
        payload = OrderCancelRequest(mix_order_id=mix_order_id)
        resp = self.__request("/api/Order/Cancel", payload)
        return is_cancel_success(resp)

    def close(self):
        """Close the underlying HTTP client session."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
