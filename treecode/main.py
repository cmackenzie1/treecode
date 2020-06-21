import argparse
import logging
from http import HTTPStatus

import boto3 as boto3

TREECODE_LENGTH = 8

HTTP_STATUS_CODE = "HTTPStatusCode"

RESPONSE_METADATA = "ResponseMetadata"

TEXT_DETECTIONS = "TextDetections"

COMMON_WORDS = {"treecode"}
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=None)
    parser.add_argument("-i", "--input", required=True, help="Path to the input file")
    return parser.parse_args()


class TextDetection:
    id: int
    detected_text: str
    confidence: float
    geometry: dict
    type: str

    def __init__(self, id_, detected_text, confidence, geometry, type_):
        self.id = id_
        self.detected_text = detected_text
        self.confidence = confidence
        self.geometry = geometry
        self.type = type_

    def to_dict(self):
        return {
            "id": self.id,
            "detected_text": self.detected_text,
            "confidence": self.confidence,
            "geometry": self.geometry,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id_=data.get("Id"),
            confidence=data.get("Confidence"),
            detected_text=data.get("DetectedText"),
            geometry=data.get("Geometry"),
            type_=data.get("Type"),
        )

    def __str__(self):
        return f"{self.detected_text}:{self.type}:{self.confidence}"

    def __repr__(self):
        return f"{self.detected_text}:{self.type}:{self.confidence}"


def is_treecode(text):
    return len(text) == TREECODE_LENGTH and text not in COMMON_WORDS


def print_treecodes(treecodes):
    print("Detected Treecodes:")
    for treecode in treecodes:
        print(f"\t- {treecode!r}")


class TreeCode:
    code: str
    confidence: float

    def __init__(self, text, confidence):
        self.text = text
        self.confidence = confidence

    def __repr__(self):
        return self.text

    def to_dict(self):
        return {"text": self.confidence, "confidence": self.confidence}

    @classmethod
    def from_dict(cls, data):
        return cls(text=data.get("text"), confidence=data.get("confidence"))


class Client:
    def __init__(self, session=None):
        self.session = session or boto3.session.Session()
        self.rekognition = self.session.client("rekognition")

    def treecode(self, bytes):
        response = self.rekognition.detect_text(**{"Image": {"Bytes": bytes}})
        if response[RESPONSE_METADATA][HTTP_STATUS_CODE] != HTTPStatus.OK:
            logger.error("Failed to communicate with Rekognition Service", response)
        text_detections = list(
            map(lambda x: TextDetection.from_dict(x), response[TEXT_DETECTIONS])
        )
        logging.debug("Text Detections: ", text_detections)
        detected_words = list(filter(lambda x: x.type == "WORD", text_detections))
        logger.debug("Detected words: ", detected_words)
        treecodes = list(
            map(
                lambda x: TreeCode(text=x.detected_text, confidence=x.confidence),
                filter(lambda x: is_treecode(x.detected_text), detected_words),
            )
        )
        return treecodes


def main(args):
    session = boto3.session.Session(profile_name=args.profile)
    treecode_client = Client(session=session)

    with open(args.input, "rb") as f:
        treecodes = treecode_client.treecode(bytes=f.read())

    print_treecodes(treecodes)
