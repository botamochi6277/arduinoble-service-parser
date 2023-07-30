from argparse import ArgumentParser
import json
import re

from logging import getLogger, DEBUG, INFO, StreamHandler, Formatter


from typing import NamedTuple


class BLECharacteristic(NamedTuple):
    name: str
    uuid: str
    data_type: str
    properties: list[str]


logger = getLogger(__file__)
handler = StreamHandler()
formatter = Formatter("%(levelname)s\t%(asctime)s  %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)


def parse_srv(txt: str):
    srv_match = re.match(
        r"[\s\S]+class ([\S]+) : public BLEService \{([\s\S]*?);[\n|\r|\n\r]\};", txt
    )
    if srv_match is None:
        logger.warning("BLEService not found")
        return
    if len(srv_match.groups()) != 2:
        logger.warning("fail to match")
        return

    srv_name = srv_match.group(1)

    logger.debug(f"Service name: {srv_name}")

    srv_statement = srv_match.group(2)

    characteristics = re.findall(r"(BLE[\S]+?Characteristic) ([\S]+?);", srv_statement)

    # logger.debug(characteristics)

    r1 = f"{srv_name}::{srv_name}\(.*?\)([\s\S]+?)" + "\{"
    constructor_succeed_txt = re.search(r1, txt)

    srv_context = re.findall(
        r"BLEService ?\(\"([a-fA-F0-9\-]+?)\"\)", constructor_succeed_txt.group()
    )
    if len(srv_context) == 0:
        logger.warning("fail to get service uuid")
        return
    logger.debug(f"service uuid: {srv_context[0]}")

    characteristic_items: list[BLECharacteristic] = []

    for chr in characteristics:
        name = chr[1]  # todo: replace with user descriptor
        data_type = chr[0].replace("BLE", "").replace("Characteristic", "")
        r2 = f'{name}\("([a-fA-F0-9\-]+?)",[ \n\t]?([\s\S]+?)\)'
        c = re.search(r2, constructor_succeed_txt.group())
        # logger.debug(c.group(1))  # characteristic uuid
        # logger.debug(c.group(2))  # characteristics property

        properties_str = c.group(2)
        properties_str = properties_str.replace("\t", "")
        properties_str = properties_str.replace(" ", "")
        properties_str = properties_str.replace("BLE", "")
        characteristic_items.append(
            BLECharacteristic(name, c.group(1), data_type, properties_str.split("|"))
        )
    logger.debug(f"characteristics: {characteristic_items}")

    service = dict(
        name=srv_name, uuid=srv_context[0], characteristics=characteristic_items
    )

    return service


def main():
    parser = ArgumentParser(description="ArduinoBLE::BLEService parser")
    parser.add_argument("filename")
    parser.add_argument("-o", "--output", default="service.json")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    with open(args.filename) as f:
        s = f.read()

    if args.verbose:
        logger.setLevel(DEBUG)

    service = parse_srv(s)
    with open(args.output, "w") as f:
        json.dump(service, f)

    logger.info(f"write {args.output}")


if __name__ == "__main__":
    logger.setLevel(INFO)
    main()
