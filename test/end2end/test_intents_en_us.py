"""End-to-end intent-routing tests for ovos-skill-easter-eggs (en-US).

Each case boots an in-process MiniCroft with the skill loaded and feeds a real
utterance through the adapt + padatious pipelines, asserting which intent the
utterance routes to. Adapt covers the keyword ``IntentBuilder`` intents; the
laws-of-robotics intent is padatious (``.intent`` samples with an ``{ordinal}``
slot). A negative case proves gibberish routes nowhere.

Run: pytest test/end2end/ -v
"""
import threading
from unittest import TestCase

from ovos_bus_client.message import Message
from ovos_bus_client.session import Session
from ovoscope import ADAPT_PIPELINE, PADATIOUS_PIPELINE, get_minicroft

SKILL_ID = "skill-easter-eggs.openvoiceos"
LANG = "en-US"
PIPELINE = ADAPT_PIPELINE + PADATIOUS_PIPELINE

# Every intent this skill registers; used to prove the negative case routes
# to none of them.
ALL_INTENTS = [
    "grandma_mode_intent",
    "adult_mode_intent",
    "stardate_intent",
    "pod_bay_doors_intent",
    "law_of_robotics.intent",
    "rock_paper_scissors_lizard_spock_intent",
    "languages_you_speak_intent",
    "portal_intent",
    "hal_intent",
    "duke_nukem_intent",
    "arnold_intent",
    "bender_intent",
    "glados_intent",
    "conan_intent",
    "bill_and_ted_intent",
    "malibu_stacey_intent",
    "sing_intent",
]


class _RoutingTest(TestCase):
    """Shared MiniCroft harness for adapt + padatious intent routing."""

    @classmethod
    def setUpClass(cls):
        cls.minicroft = get_minicroft([SKILL_ID])
        cls.bus = cls.minicroft.bus

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "minicroft", None):
            cls.minicroft.stop()

    def _emit(self, utterance):
        session = Session(f"e2e-en_us-{abs(hash(utterance))}")
        session.lang = LANG
        session.pipeline = PIPELINE
        self.bus.emit(Message(
            "recognizer_loop:utterance",
            {"utterances": [utterance], "lang": LANG},
            {"session": session.serialize()},
        ))

    def assert_matches(self, utterance, intent_name, timeout=10):
        """Assert *utterance* routes to ``{SKILL_ID}:{intent_name}``.

        Padatious intents are registered from ``.intent`` files, but the
        bus event ovos-core emits for a match drops the ``.intent``
        suffix (adapt intents have no such suffix to begin with).
        """
        matched = threading.Event()
        msg_type = f"{SKILL_ID}:{intent_name.removesuffix('.intent')}"

        def cb(_):
            matched.set()

        self.bus.on(msg_type, cb)
        try:
            self._emit(utterance)
            fired = matched.wait(timeout=timeout)
        finally:
            self.bus.remove(msg_type, cb)
        self.assertTrue(
            fired, f"{utterance!r} did not route to {intent_name!r}")

    def assert_no_match(self, utterance, timeout=5):
        """Assert *utterance* routes to none of this skill's intents."""
        fired = []
        callbacks = {}
        for intent_name in ALL_INTENTS:
            msg_type = f"{SKILL_ID}:{intent_name.removesuffix('.intent')}"
            cb = (lambda name: lambda _: fired.append(name))(intent_name)
            callbacks[msg_type] = cb
            self.bus.on(msg_type, cb)
        try:
            self._emit(utterance)
            threading.Event().wait(timeout=timeout)
        finally:
            for msg_type, cb in callbacks.items():
                self.bus.remove(msg_type, cb)
        self.assertEqual(
            fired, [], f"{utterance!r} unexpectedly routed to {fired}")


class TestAdaptIntents(_RoutingTest):
    """Keyword IntentBuilder intents matched by the adapt pipeline."""

    def test_pod_bay_doors(self):
        self.assert_matches("open the pod bay doors", "pod_bay_doors_intent")

    def test_stardate(self):
        self.assert_matches("what is the current stardate", "stardate_intent")

    def test_rock_paper_scissors_lizard_spock(self):
        self.assert_matches(
            "how to play rock paper scissors lizard spock",
            "rock_paper_scissors_lizard_spock_intent")

    def test_languages_you_speak(self):
        self.assert_matches(
            "how many languages do you speak", "languages_you_speak_intent")

    def test_hal(self):
        self.assert_matches("what would HAL 9000 say", "hal_intent")

    def test_duke_nukem(self):
        self.assert_matches("what would Duke Nukem say", "duke_nukem_intent")

    def test_arnold(self):
        self.assert_matches("what would Arnold say", "arnold_intent")

    def test_bender(self):
        self.assert_matches("what would Bender say", "bender_intent")

    def test_glados(self):
        self.assert_matches("what would GLaDOS say", "glados_intent")

    def test_malibu_stacey(self):
        self.assert_matches(
            "what would malibu stacy do", "malibu_stacey_intent")

    def test_sing(self):
        self.assert_matches("sing me a song", "sing_intent")


class TestPadatiousLawsOfRobotics(_RoutingTest):
    """Laws-of-robotics padatious intent, with and without the ordinal slot."""

    def test_all_laws(self):
        self.assert_matches(
            "what are the laws of robotics", "law_of_robotics.intent")

    def test_first_law(self):
        self.assert_matches(
            "what is the first law of robotics", "law_of_robotics.intent")


class TestNoMatch(_RoutingTest):
    """Gibberish must not route to any easter-egg intent."""

    def test_gibberish(self):
        self.assert_no_match("frobble zorp snork the wibbly")
