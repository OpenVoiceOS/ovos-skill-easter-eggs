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
from ovos_workshop.decorators import skill_api_method
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators.killable import killable_event

from .stardate import StarDate
from .constants import SPICY_SOUNDS

__author__ = "jarbas"


class EasterEggsSkill(OVOSSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def grandma_mode(self):
        return self.settings.get("grandma_mode_enabled", True)

    @intent_handler(IntentBuilder("GrandmaModeIntent").require("GrandmaMode").build())
    def handle_grandma_mode(self, _):
        self.grandma_mode = self.settings["grandma_mode_enabled"] = True
        self.speak("Ok, we'll tone it down a bit.")

    @intent_handler(IntentBuilder("AdultModeIntent").require("AdultMode").build())
    def handle_adult_mode(self, _):
        self.grandma_mode = self.settings["grandma_mode_enabled"] = False
        self.speak("Do you feel lucky, punk?")

    @intent_handler(IntentBuilder("StardateIntent").require("StardateKeyword").build())
    @killable_event
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
    @killable_event
    def handle_pod_intent(self, _):
        self.speak_dialog("pod")

    @intent_handler(
        IntentBuilder("RoboticsLawsIntent")
        .require("RoboticsKeyword")
        .require("LawKeyword")
        .optionally("LawOfRobotics")
        .build()
    )
    @killable_event
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
    @killable_event
    def handle_rock_paper_scissors_lizard_spock_intent(self, _):
        self.speak_dialog("rock_paper_scissors_lizard_spock")

    @intent_handler(IntentBuilder("LanguagesYouSpeakIntent").require("LanguagesYouSpeakKeyword").build())
    def handle_number_of_languages_intent(self, _):
        self.speak_dialog("languages")

    @intent_handler(IntentBuilder("PortalIntent").require("PortalKeyword").build())
    @killable_event
    def handle_portal_intent(self, _):
        path, files = self.get_reference_files("/sounds/portal", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(mp3)
        else:
            self.speak_dialog("bad_file")

    def get_reference_files(self, path_ending, extension):
        path = dirname(__file__) + path_ending
        if self.grandma_mode:
            files = [sound for sound in listdir(path) if f".{extension}" in sound and sound not in SPICY_SOUNDS]
        else:
            files = [sound for sound in listdir(path) if f".{extension}" in sound]
        return path, files

    @intent_handler(IntentBuilder("HALIntent").require("HALKeyword").build())
    @killable_event
    def handle_hal_intent(self, _):
        path, files = self.get_reference_files("/sounds/hal", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(mp3)
        else:
            self.speak_dialog("bad_file")

    @intent_handler(IntentBuilder("DukeNukemIntent").require("DukeNukemKeyword").build())
    @killable_event
    def handle_dukenukem_intent(self, _):
        if not self.grandma_mode:
            path, files = self.get_reference_files("/sounds/dukenukem", "wav")
            if len(files):
                wav = path + "/" + random.choice(files)
                self.play_audio(wav)
            else:
                self.speak_dialog("bad_file")
        else:
            self.speak("Duke Who-Kem?")

    @intent_handler(IntentBuilder("ArnoldIntent").require("ArnoldKeyword").build())
    @killable_event
    def handle_arnold_intent(self, _):
        path, files = self.get_reference_files("/sounds/arnold", "wav")
        if len(files):
            wav = path + "/" + random.choice(files)
            self.play_audio(wav)
        else:
            self.speak_dialog("bad_file")

    @intent_handler(IntentBuilder("BenderIntent").require("BenderKeyword").build())
    @killable_event
    def handle_bender_intent(self, _):
        path, files = self.get_reference_files("/sounds/bender", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(mp3)
        else:
            self.speak_dialog("bad_file")

    @intent_handler(IntentBuilder("GladosIntent").require("GladosKeyword").build())
    @killable_event
    def handle_glados_intent(self, _):
        path, files = self.get_reference_files("/sounds/glados", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(mp3)
        else:
            self.speak_dialog("bad_file")

    @skill_api_method
    def get_display_date(self):
        return StarDate().getStardate()
