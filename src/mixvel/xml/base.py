from __future__ import annotations

from typing import ClassVar
from xml.etree import ElementTree as ET

from mixvel._compat.pydantic import BaseModel, ConfigDict


class XmlMessage(BaseModel):
    """Base class for serializable MixVel XML messages."""

    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)

    XML_TAG: ClassVar[str]
    XML_NS_MAP: ClassVar[dict[str, str]] = {}

    def to_xml_element(self) -> ET.Element:
        element = ET.Element(self.XML_TAG)
        for prefix, uri in self.XML_NS_MAP.items():
            attr_name = f"xmlns:{prefix}" if prefix else "xmlns"
            element.set(attr_name, uri)
        self._build_body(element)
        return element

    def to_xml(self) -> str:
        return ET.tostring(self.to_xml_element(), encoding="unicode")

    def _build_body(self, element: ET.Element) -> None:  # pragma: no cover - abstract
        raise NotImplementedError
