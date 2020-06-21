import argparse
import enum
from base64 import b64encode
from http import HTTPStatus
from pprint import pprint

import boto3 as boto3

import logging

TREECODE_LENGTH = 8

HTTP_STATUS_CODE = 'HTTPStatusCode'

RESPONSE_METADATA = 'ResponseMetadata'

TEXT_DETECTIONS = 'TextDetections'

COMMON_WORDS = {'treecode'}
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
        return cls(id_=data.get("Id"),
                   confidence=data.get("Confidence"),
                   detected_text=data.get("DetectedText"),
                   geometry=data.get("Geometry"),
                   type_=data.get("Type"))

    def __str__(self):
        return f"{self.detected_text}:{self.type}:{self.confidence}"

    def __repr__(self):
        return f"{self.detected_text}:{self.type}:{self.confidence}"


def is_treecode(text_detection):
    return len(text_detection.detected_text) == TREECODE_LENGTH and text_detection.detected_text not in COMMON_WORDS


def main(args):
    session = boto3.session.Session(profile_name=args.profile)
    rekognition = session.client("rekognition")

    with open(args.input, "rb") as f:
        response = rekognition.detect_text(**{
            "Image": {
                "Bytes": f.read()
            }
        })
    if response[RESPONSE_METADATA][HTTP_STATUS_CODE] != HTTPStatus.OK:
        logger.error("Failed to communicate with Rekognition Service", response)

    text_detections = list(map(lambda x: TextDetection.from_dict(x), response[TEXT_DETECTIONS]))
    print("Text Detections: ", text_detections)
    detected_lines = list(filter(lambda x: x.type == "LINE", text_detections))
    detected_words = list(filter(lambda x: x.type == "WORD", text_detections))
    print("Detected Lines: ", detected_lines)
    print("Detected words: ", detected_words)
    treecodes = list(filter(is_treecode, detected_words))
    print("Treecodes :", treecodes)


if __name__ == '__main__':
    main(parse_args())
