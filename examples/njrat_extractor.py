#!/usr/bin/env python3
"""
Extracts the configuration of the NjRAT malware.
"""
from argparse import ArgumentParser
from base64 import b64decode
from json import dumps

from malnetlib.models import DotNetPE


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("sample", help="Path to the sample file.")
    args = parser.parse_args()

    pe = DotNetPE(args.sample)
    ok_class = pe.get_object("OK")
    njrat_conf = {
        "host": ok_class.get_attribute("HH").get_value(),
        "port": ok_class.get_attribute("P").get_value(),
        "install_directory": "%" + ok_class.get_attribute("DR").get_value() + "%",
        "install_name": ok_class.get_attribute("EXE").get_value(),
        "startup": ok_class.get_attribute("sf").get_value(),
        "campain_id": b64decode(ok_class.get_attribute("VN").get_value()).decode("UTF-8"),
        "version": ok_class.get_attribute("VR").get_value(),
        "network_separator": ok_class.get_attribute("Y").get_value(),
        "mutex": ok_class.get_attribute("RG").get_value()
    }
    print(dumps(njrat_conf))
