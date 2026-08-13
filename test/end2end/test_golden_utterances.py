"""Golden-utterance end-to-end coverage for ovos-skill-easter-eggs (en-US).

Follows the pattern merged in ovos-skill-volume's ``test/end2end/`` suite: a
vendored ``golden_utterances.jsonl`` corpus, one module-scoped ``MiniCroft``,
one parametrized test item per row.

None of this skill's handlers block on a follow-up ``get_response()`` for the
utterances covered here, but capture still ends at
``mycroft.skill.handler.start`` (right after the intent binding fires, before
the handler body runs) rather than ``ovos.utterance.handled``, matching the
volume suite's convention: the assertion under test is the intent routing,
not the handler's side effects (which vary with sound-file availability,
grandma_mode setting, TTS backend, etc).
"""
import json
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

_IGNORE = [
    "speak",
    "ovos.utterance.speak",
    "mycroft.audio.play_sound",
]

GOLDEN_PATH = Path(__file__).parent / "golden_utterances.jsonl"

# utterances lifted verbatim from other skills' domains, picked for lexical
# overlap with easter-eggs vocabulary ("say", "sing", "song", "open the
# doors", numbers/ordinals) to check they are not falsely claimed.
NEGATIVE_UTTERANCES = [
    ("play some music", "ovos-skill-music.openvoiceos"),
    ("sing me the weather forecast", "ovos-skill-weather.openvoiceos"),
    ("open the garage doors", "ovos-skill-homeassistant.openvoiceos"),
    ("what's the weather today", "ovos-skill-weather.openvoiceos"),
    ("set a timer for 5 minutes", "ovos-skill-alerts.openvoiceos"),
    ("what time is it", "ovos-skill-date-time.openvoiceos"),
]


def _candidates(skill_id: str, intent_label: str) -> set:
    """Different padatious/padacioso plugin versions register the
    matched-intent bus event under different normalizations of the
    ``.intent`` filename basename -- observed variants include the bare
    basename with no extension (current OVOS-INTENT-2 naming, see
    ovos-skill-parrot#119) and the basename with the extension kept (older
    naming). ovos-padatious isn't installed in this environment (heavy
    native/swig dependency) so padatious falls through to padacioso, which
    matches under the newer unsuffixed name -- candidates cover both so the
    suite isn't pinned to whichever pipeline plugin happens to be
    installed."""
    base = intent_label[:-len(".intent")] if intent_label.endswith(".intent") else intent_label
    return {f"{skill_id}:{intent_label}", f"{skill_id}:{base}"}


def _load_golden_rows():
    rows = []
    with open(GOLDEN_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("needs_manual"):
                continue
            rows.append(row)
    return rows


GOLDEN_ROWS = [pytest.param(r, id=r["utterance"]) for r in _load_golden_rows()]


@pytest.fixture(scope="module")
def minicroft():
    mc = get_minicroft([SKILL_ID])
    yield mc
    mc.stop()


def _types(mc, text, session_id):
    session = Session(session_id)
    session.lang = LANG
    session.pipeline = list(_PIPELINE)
    # blacklisted_intents defaults to None on a fresh Session, which crashes
    # the padacioso pipeline (NoneType membership test) - force an empty list.
    session.blacklisted_intents = []
    utterance = Message(
        "recognizer_loop:utterance",
        {"utterances": [text], "lang": LANG},
        {"session": session.serialize(), "source": "A", "destination": "B"},
    )
    capture = CaptureSession(
        mc,
        eof_msgs=["mycroft.skill.handler.start"],
        ignore_messages=_IGNORE,
    )
    capture.capture(utterance, timeout=30)
    return [m.msg_type for m in capture.finish()]


def _golden_id(row):
    return row["utterance"]


@pytest.mark.timeout(60)
@pytest.mark.parametrize("row", GOLDEN_ROWS, ids=_golden_id)
def test_golden_utterance(minicroft, row):
    candidates = _candidates(SKILL_ID, row["intent_label"])
    types = _types(minicroft, row["utterance"], f"golden-{_golden_id(row)}")
    assert any(t in candidates for t in types), (
        f"{row['utterance']!r}: expected one of {sorted(candidates)!r}, got {types!r}"
    )


@pytest.mark.timeout(60)
@pytest.mark.parametrize("negative", NEGATIVE_UTTERANCES, ids=lambda n: n[0])
def test_negative_confusable_not_claimed(minicroft, negative):
    text, source_skill = negative
    types = _types(minicroft, text, f"negative-{text}")
    claimed = any(t.startswith(f"{SKILL_ID}:") for t in types)
    assert not claimed, f"{text!r} (from {source_skill}) was incorrectly claimed by {SKILL_ID}"
