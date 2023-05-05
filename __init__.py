# pylint: disable=unused-import,missing-docstring,invalid-name
# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

import random
from os import listdir
from os.path import dirname

from ovos_utils.intents import IntentBuilder
from mycroft import intent_handler
from ovos_workshop.skills import OVOSSkill

from .stardate import StarDate

__author__ = "jarbas"


class EasterEggsSkill(OVOSSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @intent_handler(IntentBuilder("StardateIntent").require("StardateKeyword").build())
    def handle_stardate_intent(self, _):
        spoken_stardate = self._create_spoken_stardate()
        self.speak_dialog("stardate", {"stardate": spoken_stardate})

    def _create_spoken_stardate(self):
        spoken_stardate = ""
        sd = str(StarDate().getStardate())
        for x in sd:
            if x.isnumeric():
                spoken_stardate += f"{x} "
            if x == ".":
                spoken_stardate += "point "
        return spoken_stardate

    @intent_handler(IntentBuilder("PodBayDoorsIntent").require("PodBayDoorsKeyword").build())
    def handle_pod_intent(self, _):
        self.speak_dialog("pod")

    @intent_handler(
        IntentBuilder("RoboticsLawsIntent")
        .require("RoboticsKeyword")
        .require("LawKeyword")
        .optionally("LawOfRobotics")
        .build()
    )
    def handle_robotic_laws_intent(self, message):
        law = str(message.data.get("LawOfRobotics", "all"))
        if law == "1":
            self.speak_dialog("rule1")
        elif law == "2":
            self.speak_dialog("rule2")
        elif law == "3":
            self.speak_dialog("rule3")
        else:
            self.speak_dialog("rule1")
            self.speak_dialog("rule2")
            self.speak_dialog("rule3")

    @intent_handler(
        IntentBuilder("rock_paper_scissors_lizard_spock_Intent")
        .require("rock_paper_scissors_lizard_spock_Keyword")
        .build()
    )
    def handle_rock_paper_scissors_lizard_spock_intent(self, _):
        self.speak_dialog("rock_paper_scissors_lizard_spock")

    @intent_handler(IntentBuilder("LanguagesYouSpeakIntent").require("LanguagesYouSpeakKeyword").build())
    def handle_number_of_languages_intent(self, _):
        self.speak_dialog("languages")

    @intent_handler(IntentBuilder("PortalIntent").require("PortalKeyword").build())
    def handle_portal_intent(self, _):
        path = dirname(__file__) + "/sounds/portal"
        files = [mp3 for mp3 in listdir(path) if ".mp3" in mp3]
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(mp3)
        else:
            self.speak_dialog("bad_file")

    @intent_handler(IntentBuilder("HALIntent").require("HALKeyword").build())
    def handle_hal_intent(self, _):
        path = dirname(__file__) + "/sounds/hal"
        files = [mp3 for mp3 in listdir(path) if ".mp3" in mp3]
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(mp3)
        else:
            self.speak_dialog("bad_file")

    @intent_handler(IntentBuilder("DukeNukemIntent").require("DukeNukemKeyword").build())
    def handle_dukenukem_intent(self, _):
        path = dirname(__file__) + "/sounds/dukenukem"
        files = [wav for wav in listdir(path) if ".wav" in wav]
        if len(files):
            wav = path + "/" + random.choice(files)
            self.play_audio(wav)
        else:
            self.speak_dialog("bad_file")

    @intent_handler(IntentBuilder("ArnoldIntent").require("ArnoldKeyword").build())
    def handle_arnold_intent(self, _):
        path = dirname(__file__) + "/sounds/arnold"
        files = [wav for wav in listdir(path) if ".wav" in wav]
        if len(files):
            wav = path + "/" + random.choice(files)
            self.play_audio(wav)
        else:
            self.speak_dialog("bad_file")

    @intent_handler(IntentBuilder("BenderIntent").require("BenderKeyword").build())
    def handle_bender_intent(self, _):
        path = dirname(__file__) + "/sounds/bender"
        files = [mp3 for mp3 in listdir(path) if ".mp3" in mp3]
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(mp3)
        else:
            self.speak_dialog("bad_file")

    @intent_handler(IntentBuilder("GladosIntent").require("GladosKeyword").build())
    def handle_glados_intent(self, _):
        path = dirname(__file__) + "/sounds/glados"
        files = [mp3 for mp3 in listdir(path) if ".mp3" in mp3]
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(mp3)
        else:
            self.speak_dialog("bad_file")

    def stop(self):
        pass


def create_skill():
    return EasterEggsSkill()
