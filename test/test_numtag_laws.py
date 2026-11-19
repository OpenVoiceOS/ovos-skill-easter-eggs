"""The ordinal of "the third law of robotics" is read in every locale that has a numtag lexicon.

Each row is a phrase of the locale's own law_of_robotics.intent. padacioso
cuts the ordinal out of the phrase; the handler must speak the law a speaker
asks for. The gold is the position the words name, not a parser result.
"""
from os.path import dirname, join
from unittest.mock import MagicMock, PropertyMock, call, patch

import pytest
from ovos_bus_client.message import Message
from padacioso import IntentContainer

from skill_easter_eggs import EasterEggsSkill

LOCALE = join(dirname(dirname(__file__)), "locale")

# (locale dir, skill lang, utterance, law)
ROWS = [
    ("ca-ES", "ca-es", "digues la primera llei de la robòtica", 1),
    ("ca-ES", "ca-es", "digues la segona llei de la robòtica", 2),
    ("ca-ES", "ca-es", "digues la tercera llei de la robòtica", 3),
    ("da-DK", "da-dk", "sig den første robotlov", 1),
    ("da-DK", "da-dk", "sig den anden robotlov", 2),
    ("da-DK", "da-dk", "sig den tredje robotlov", 3),
    ("de-DE", "de-de", "was ist das erste gesetz der robotik", 1),
    ("de-DE", "de-de", "was ist das zweite gesetz der robotik", 2),
    ("de-DE", "de-de", "was ist das dritte gesetz der robotik", 3),
    ("en-US", "en-us", "what is the first law of robotics", 1),
    ("en-US", "en-us", "what is the second law of robotics", 2),
    ("en-US", "en-us", "what is the third law of robotics", 3),
    ("en-US", "en-us", "what is the 3rd law of robotics", 3),
    ("es-ES", "es-es", "dime la primera ley de la robótica", 1),
    ("es-ES", "es-es", "dime la segunda ley de la robótica", 2),
    ("es-ES", "es-es", "dime la tercera ley de la robótica", 3),
    ("eu-ES", "eu-es", "zein da robotikaren lehenengo legea", 1),
    ("eu-ES", "eu-es", "zein da robotikaren bigarren legea", 2),
    ("eu-ES", "eu-es", "zein da robotikaren hirugarren legea", 3),
    ("fr-FR", "fr-fr", "quelle est la première loi de la robotique", 1),
    ("fr-FR", "fr-fr", "quelle est la deuxième loi de la robotique", 2),
    ("fr-FR", "fr-fr", "quelle est la troisième loi de la robotique", 3),
    ("gl-ES", "gl-es", "cal é a primeira lei da robótica", 1),
    ("gl-ES", "gl-es", "cal é a segunda lei da robótica", 2),
    ("gl-ES", "gl-es", "cal é a terceira lei da robótica", 3),
    ("it-IT", "it-it", "qual è la prima legge della robotica", 1),
    ("it-IT", "it-it", "qual è la seconda legge della robotica", 2),
    ("it-IT", "it-it", "qual è la terza legge della robotica", 3),
    ("kab", "kab", "ini-yi-d asaḍuf wis kraḍ n tsenṛubut", 3),
    ("nl-NL", "nl-nl", "wat is de eerste wet van de robotica", 1),
    ("nl-NL", "nl-nl", "wat is de tweede wet van de robotica", 2),
    ("nl-NL", "nl-nl", "wat is de derde wet van de robotica", 3),
    ("oc-FR", "oc-fr", "quina es la primièra lei de la robotica", 1),
    ("oc-FR", "oc-fr", "quina es la segonda lei de la robotica", 2),
    ("oc-FR", "oc-fr", "quina es la tresena lei de la robotica", 3),
    ("pt-BR", "pt-br", "qual é a primeira lei da robótica", 1),
    ("pt-BR", "pt-br", "qual é a segunda lei da robótica", 2),
    ("pt-BR", "pt-br", "qual é a terceira lei da robótica", 3),
    ("pt-PT", "pt-pt", "qual é a primeira lei da robótica", 1),
    ("pt-PT", "pt-pt", "qual é a segunda lei da robótica", 2),
    ("pt-PT", "pt-pt", "qual é a terceira lei da robótica", 3),
    ("sv-SE", "sv-se", "vad är den första robotlagen", 1),
    ("sv-SE", "sv-se", "vad är den andra robotlagen", 2),
    ("sv-SE", "sv-se", "vad är den tredje robotlagen", 3),
]


def _slot(locale, utterance):
    with open(join(LOCALE, locale, "vocab", "law_of_robotics.intent"), encoding="utf-8") as f:
        container = IntentContainer()
        container.add_intent("law_of_robotics", f.read().splitlines())
    match = container.calc_intent(utterance)
    assert match["name"] == "law_of_robotics", (utterance, match)
    return match["entities"]["ordinal"]


def _ask(lang, ordinal):
    skill = object.__new__(EasterEggsSkill)
    skill.speak_dialog = MagicMock()
    skill.log = MagicMock()
    with patch.object(EasterEggsSkill, "lang", new_callable=PropertyMock, return_value=lang):
        skill.handle_robotic_laws_intent(Message("test", {"ordinal": ordinal}))
    return skill.speak_dialog.call_args_list


@pytest.mark.parametrize("locale,lang,utterance,law", ROWS)
def test_the_spoken_law_is_the_one_asked_for(locale, lang, utterance, law):
    assert _ask(lang, _slot(locale, utterance)) == [call(f"rule{law}")]


@pytest.mark.parametrize("ordinal", ["fourth", "4th", "tenth"])
def test_a_law_that_does_not_exist_is_invalid(ordinal):
    assert _ask("en-us", ordinal) == [call("invalid_law")]


@pytest.mark.parametrize("ordinal", ["", "gibberish"])
def test_no_ordinal_recites_all_three(ordinal):
    assert _ask("en-us", ordinal) == [call("rule1"), call("rule2"), call("rule3")]
