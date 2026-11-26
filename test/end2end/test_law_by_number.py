"""The robotics-law intent reads the law number from an ordinal word or a digit."""
from pathlib import Path

import pytest
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession, get_minicroft

SKILL_ID = "skill-easter-eggs.openvoiceos"
LOCALE = Path(__file__).parents[2] / "locale"

CASES = [
    ("en-US", "what is the second law of robotics"),
    ("en-US", "what is the 2 law of robotics"),
    ("pt-PT", "qual é a segunda lei da robótica"),
    ("pt-PT", "qual é a 2 lei da robótica"),
    ("fr-FR", "quelle est la deuxième loi de la robotique"),
    ("fr-FR", "quelle est la 2 loi de la robotique"),
]


@pytest.fixture(scope="module")
def minicroft():
    mc = get_minicroft([SKILL_ID], lang="en-US", secondary_langs=["pt-PT", "fr-FR"])
    yield mc
    mc.stop()


def _spoken(mc, text, lang):
    session = Session(f"law-{lang}-{text}")
    session.lang = lang
    session.pipeline = ["ovos-padacioso-pipeline-plugin"]
    message = Message(
        "recognizer_loop:utterance",
        {"utterances": [text], "lang": lang},
        {"session": session.serialize(), "source": "A", "destination": "B"},
    )
    capture = CaptureSession(mc, eof_msgs=["ovos.utterance.handled"], ignore_messages=[])
    capture.capture(message, timeout=30)
    msgs = capture.finish()
    return [m.data["utterance"] for m in msgs
            if m.msg_type == "ovos.utterance.speak"]


@pytest.mark.timeout(60)
@pytest.mark.parametrize("lang,text", CASES)
def test_second_law_is_spoken(minicroft, lang, text):
    rule2 = (LOCALE / lang / "dialog" / "rule2.dialog").read_text(encoding="utf-8").strip()
    assert _spoken(minicroft, text, lang) == [rule2]


@pytest.mark.timeout(60)
@pytest.mark.xfail(
    strict=True,
    reason="DEFECT: locale/en-US/dialog/rule3.dialog holds all three laws, not the Third Law only",
)
def test_third_law_is_spoken_alone(minicroft):
    assert _spoken(minicroft, "what is the third law of robotics", "en-US") == [
        "A robot must protect its own existence as long as such protection "
        "does not conflict with the First or Second Laws."
    ]
