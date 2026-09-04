"""Intent-routing parity tests for the en-US locale.

The skill's Adapt `IntentBuilder` intents were migrated to lang-agnostic
`.intent` files. These tests load the actual `locale/en-US/vocab/*.intent`
resources through `padacioso.IntentContainer` (the same engine syntax the
skill's own `law_of_robotics.intent` already used) and assert every
phrasing the old Adapt keyword vocabs matched still routes to the correct
intent, plus a handful of sibling-confusion negatives between intents that
share vocabulary (e.g. "sing"/"song" appearing in both `sing_intent` and
`portal_intent`).

This stays in the skill's existing FakeBus/unit-test style: no ovoscope
end-to-end MiniCroft is spun up, only the resource files themselves are
exercised against the matching engine.
"""
from glob import glob
from os.path import basename, dirname, join

import pytest
import yaml
from padacioso import IntentContainer

LOCALE_DIR = join(dirname(dirname(__file__)), "locale", "en-US", "vocab")


def _load_container():
    container = IntentContainer()
    for path in glob(join(LOCALE_DIR, "*.intent")):
        name = basename(path)[: -len(".intent")]
        with open(path, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        container.add_intent(name, lines)
    return container


def _load_gold_phrases():
    """Load the en-US phrasings from test_intents.yaml (the pre-existing
    Adapt-era acceptance list) as (intent, utterance) pairs."""
    with open(join(dirname(__file__), "test_intents.yaml"), encoding="utf-8") as f:
        data = yaml.safe_load(f)
    en_us = data["en-US"]
    pairs = []
    for intent, utterances in en_us.items():
        base = intent[: -len(".intent")] if intent.endswith(".intent") else intent
        for utterance in utterances:
            pairs.append((base, utterance))
    return pairs


@pytest.fixture(scope="module")
def container():
    return _load_container()


GOLD_PHRASES = _load_gold_phrases()


@pytest.mark.parametrize("intent,utterance", GOLD_PHRASES)
def test_gold_utterance_routes_to_expected_intent(container, intent, utterance):
    match = container.calc_intent(utterance)
    assert match is not None, f"{utterance!r} matched no intent"
    assert match["name"] == intent, (
        f"{utterance!r} routed to {match['name']!r}, expected {intent!r}"
    )


@pytest.mark.parametrize(
    "utterance,not_intent",
    [
        # "sing"/"song" appear in both portal_intent and sing_intent samples
        ("sing", "portal_intent"),
        ("sing me a song", "portal_intent"),
        ("sing portal", "sing_intent"),
        # arnold/terminator/schwarzenegger say vs generic "say" siblings
        ("arnold say", "bender_intent"),
        ("bender say", "arnold_intent"),
        # bare "stardate" family must not bleed into pod bay doors
        ("stardate", "pod_bay_doors_intent"),
        # adult vs grandma mode toggles are mutually exclusive
        ("hurt me plenty", "grandma_mode_intent"),
        ("too young to die", "adult_mode_intent"),
    ],
)
def test_sibling_confusion_negatives(container, utterance, not_intent):
    match = container.calc_intent(utterance)
    matched_name = match["name"] if match else None
    assert matched_name != not_intent, (
        f"{utterance!r} unexpectedly routed to {not_intent!r}"
    )


if __name__ == "__main__":
    pytest.main()
