# -*- coding: utf-8 -*-
import os
from xml.etree import ElementTree as ET

from mixvel.utils import strip_namespaces

here = os.path.abspath(os.path.dirname(__file__))


def parse_xml(path):
    """Return an ElementTree root loaded from the source path."""

    abs_path = os.path.join(here, path)
    tree = ET.parse(abs_path)
    return tree.getroot()


def parse_xml_response(resp_path):
    """Return a clean XML API response from the given file."""

    resp = parse_xml(resp_path)
    strip_namespaces(resp)
    return resp.find('.//Body/AppData/')
