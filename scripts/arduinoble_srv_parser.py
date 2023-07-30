from argparse import ArgumentParser

import re

from logging import getLogger, DEBUG, INFO, StreamHandler, Formatter

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

    logger.debug(characteristics)


def main():
    parser = ArgumentParser(description="ArduinoBLE::BLEService parser")
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename) as f:
        s = f.read()
    parse_srv(s)


if __name__ == "__main__":
    logger.setLevel(DEBUG)
    main()
