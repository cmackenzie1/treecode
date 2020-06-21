from unittest import TestCase

from treecode.main import TextDetection


class TestTextDetection(TestCase):
    def test_to_dict(self):
        text_detection = TextDetection(
            id_=1, detected_text="Hello", confidence=99.0, type_="LINE", geometry={}
        )
        self.assertDictEqual(
            {
                "id": 1,
                "detected_text": "Hello",
                "confidence": 99.0,
                "geometry": {},
                "type": "LINE",
            },
            text_detection.to_dict(),
        )

    def test_from_dict(self):
        text_detection_dict = {
            "Id": 1,
            "DetectedText": "Hello",
            "Confidence": 99.0,
            "Geometry": {},
            "Type": "LINE",
        }
        text_detection = TextDetection.from_dict(text_detection_dict)
