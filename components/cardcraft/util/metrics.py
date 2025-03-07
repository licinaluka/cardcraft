import csv
import json
import os.path
import time
import unittest
import xml.etree.ElementTree as ET

check: unittest.TestCase = unittest.TestCase()


def record(subject: str, verb: str, _object: str) -> bool:
    with check.assertRaises(
        json.JSONDecodeError, msg="Input must not be structured data, JSON was given"
    ):
        json.loads(_object)

    with check.assertRaises(
        ET.ParseError, msg="Input must not be structured data, XML was given"
    ):
        ET.fromstring(_object)

    with check.assertRaises(
        IndexError, msg="Input must not be structured data, multiline text was given"
    ):
        _object.split("\n")[1]

    spreadsheet: str = os.path.join(os.environ["HOME"], "cardcraft.metrics.csv")

    if not os.path.exists(spreadsheet):
        with open(spreadsheet, "a") as f:
            pass

    with open(spreadsheet, "a") as f:
        csv.DictWriter(
            f, fieldnames=["subject", "verb", "object", "timestamp"]
        ).writerow(
            {
                "subject": subject,
                "verb": verb,
                "object": _object,
                "timestamp": time.time(),
            }
        )
