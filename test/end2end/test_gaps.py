"""Strict xfail tests documenting known gaps between the shipped locale
resources and the skill's actual handler wiring, found while building the
golden e2e suite. These are documented, not fixed, per the tests-only scope
of this PR (see PR description).

xfail(strict=True) means: if the underlying handler is later fixed to close
the gap, this test starts *passing* unexpectedly and CI fails loudly,
forcing the xfail marker to be removed/updated instead of silently rotting.
"""
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


@pytest.fixture(scope="module")
def minicroft():
    mc = get_minicroft([SKILL_ID])
    yield mc
    mc.stop()


def _speak_dialogs(mc, text, session_id):
    """Fire an utterance and return the ``meta.dialog`` name of every
    ``ovos.utterance.speak`` message emitted while the handler runs."""
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
    messages = capture.finish()
    return [
        m.data.get("meta", {}).get("dialog")
        for m in messages
        if m.msg_type == "ovos.utterance.speak"
    ]


@pytest.mark.timeout(60)
@pytest.mark.xfail(
    strict=True,
    reason=(
        "GAP: locale/en-US/dialog/rule0.dialog (the Zeroth Law of Robotics) "
        "ships as a resource but is never spoken. handle_robotic_laws_intent "
        "(__init__.py) only ever calls speak_dialog('rule1'/'rule2'/'rule3') "
        "or 'invalid_law' -- there is no branch for law == '0'. Separately, "
        "extract_number('zeroth', ordinals=True) does not resolve 'zeroth' "
        "to a number, so 'what is the zeroth law of robotics' falls into "
        "the `if not law` branch and recites all three laws instead of "
        "either speaking rule0 or invalid_law. rule0.dialog is effectively "
        "dead content. Not fixed here (tests-only PR); documented in the "
        "PR description as a finding."
    ),
)
def test_zeroth_law_is_unreachable(minicroft):
    dialogs = _speak_dialogs(minicroft, "what is the zeroth law of robotics", "gap-zeroth-law")
    assert dialogs == ["rule0"], (
        f"expected the Zeroth Law dialog to be spoken, got {dialogs!r} "
        "(if this now passes, handle_robotic_laws_intent has been fixed to "
        "wire up rule0.dialog -- remove this xfail)"
    )
