from argparse import ArgumentParser

import re


def parse_srv(txt: str):
    srv_match = re.match(
        r"[\s\S]+class ([\S]+) : public BLEService \{([\s\S]*?);[\n|\r|\n\r]\};", txt
    )
    if srv_match is None:
        print("BLEService not found")
        return
    if len(srv_match.groups()) != 2:
        print("fail to match")

    srv_name = srv_match.group(1)

    print(f"Service name: {srv_name}")

    srv_statement = srv_match.group(2)

    print(f"context: {srv_match.group(2)}")


def main():
    parser = ArgumentParser(description="ArduinoBLE::BLEService parser")
    parser.add_argument("filename")
    args = parser.parse_args()

    with open(args.filename) as f:
        s = f.read()
    parse_srv(s)


if __name__ == "__main__":
    main()
