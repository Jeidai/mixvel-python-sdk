from __future__ import annotations

import datetime as _dt
from xml.etree import ElementTree as ET

from .base import XmlMessage
from .helpers import format_text


class MessageInfo(XmlMessage):
    XML_TAG = "MessageInfo"

    message_id: str
    time_sent: _dt.datetime

    def _build_body(self, element: ET.Element) -> None:
        element.set("MessageId", self.message_id)
        element.set("TimeSent", format_text(self.time_sent))


class MessageEnvelope(XmlMessage):
    XML_TAG = "MixEnv:Envelope"
    XML_NS_MAP = {"MixEnv": "https://www.mixvel.com/API/XSD/mixvel_envelope/1_06"}

    message_info: MessageInfo
    payload: XmlMessage

    def _build_body(self, element: ET.Element) -> None:
        ET.SubElement(element, "Header")
        body = ET.SubElement(element, "Body")
        body.append(self.message_info.to_xml_element())
        app_data = ET.SubElement(body, "AppData")
        app_data.append(self.payload.to_xml_element())
