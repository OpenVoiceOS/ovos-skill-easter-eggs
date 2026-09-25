"""Fixed-prompt / fixed-response effect coverage for
ovos-skill-easter-eggs (en-US).

``test_golden_utterances.py`` only asserts that an utterance routes to the
expected intent (capture ends at ``mycroft.skill.handler.start``, before the
handler body runs), so a handler that raises, speaks nothing, or speaks the
wrong dialog still passes there. The three prompts covered here have a
single fixed textual response apiece -- no sound file, no random branch, no
external state -- so the actual spoken text is asserted against the
skill's own ``locale/en-US/dialog/*.dialog`` file, read directly rather than
retyped here. A handler returning a constant pulled from the wrong dialog
file (e.g. ``invalid_law`` instead of ``rock_paper_scissors_lizard_spock``)
passes a "some text was spoken" check and fails this one.
"""
from pathlib import Path

import pytest
from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import CaptureSession, get_minicroft

SKILL_ID = "skill-easter-eggs.openvoiceos"
LANG = "en-US"

_PIPELINE = [
    "ovos-adapt-pipeline-plugin",
    "ovos-padacioso-pipeline-plugin",
]

DIALOG_DIR = Path(__file__).parent.parent.parent / "locale" / "en-US" / "dialog"


def _dialog_lines(name: str) -> list:
    """The candidate set of exact spoken texts for a dialog file, read
    directly from the file that ships -- a rewording does not desync the
    expected text from what the skill actually speaks."""
    path = DIALOG_DIR / f"{name}.dialog"
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


FIXED_RESPONSE_CASES = [
    ("open the pod bay doors", "pod"),
    ("rock paper scissors lizard spock", "rock_paper_scissors_lizard_spock"),
    ("languages can you speak", "languages"),
]


@pytest.fixture(scope="module")
def minicroft():
    mc = get_minicroft([SKILL_ID])
    yield mc
    mc.stop()


def _spoken_texts(mc, text, session_id):
    session = Session(session_id)
    session.lang = LANG
    session.pipeline = list(_PIPELINE)
    session.blacklisted_intents = []
    utterance = Message(
        "recognizer_loop:utterance",
        {"utterances": [text], "lang": LANG},
        {"session": session.serialize(), "source": "A", "destination": "B"},
    )
    capture = CaptureSession(
        mc,
        eof_msgs=["ovos.utterance.handled"],
        ignore_messages=[],
    )
    capture.capture(utterance, timeout=30)
    return [
        m.data.get("utterance")
        for m in capture.finish()
        if m.msg_type == "ovos.utterance.speak"
    ]


@pytest.mark.timeout(60)
@pytest.mark.parametrize("case", FIXED_RESPONSE_CASES, ids=lambda c: c[0])
def test_fixed_response_matches_locale_dialog(minicroft, case):
    utterance, dialog_name = case
    lines = _dialog_lines(dialog_name)
    assert len(lines) == 1, (
        f"{dialog_name}.dialog has {len(lines)} candidate lines; this case "
        "assumes a single fixed response, use membership for a multi-line file"
    )
    expected = lines[0]
    spoken = _spoken_texts(minicroft, utterance, f"fixed-{utterance}")
    assert spoken == [expected], (
        f"{utterance!r}: expected exactly [{expected!r}] "
        f"(from {dialog_name}.dialog), got {spoken!r}"
    )
