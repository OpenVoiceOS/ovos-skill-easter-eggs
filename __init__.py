# pylint: disable=unused-import,missing-docstring,invalid-name
import random
from datetime import datetime
from dateutil.tz import gettz
from os import listdir
from os.path import dirname

from lingua_franca.time import default_timezone
from ovos_bus_client.message import Message
from ovos_bus_client.util.scheduler import EventScheduler
from ovos_mark1_utils.faceplate import FallingDots
from ovos_workshop.decorators import skill_api_method, intent_handler
from ovos_workshop.skills import OVOSSkill
from ovos_utils.intents import IntentBuilder

from .stardate import StarDate
from .constants import ANNUAL, ASCII_SNOW, SPICY_SOUNDS


class EasterEggsSkill(OVOSSkill):
    def __init__(self, *args, bus=None, **kwargs):
        super().__init__(bus=bus, *args, **kwargs)
        self._event_scheduler = EventScheduler(bus=self.bus)
        self.bus.on(f"{self.skill_id}.christmas_day", self.handle_christmas_day)
        self._set_easter_egg_events()

    @property
    def event_scheduler(self) -> EventScheduler:
        """
        Get the EventScheduler that tracks all Alert objects and their statuses.
        """
        if not self._event_scheduler:
            raise RuntimeError("Requested EventScheduler before initialize")
        return self._event_scheduler

    @property
    def grandma_mode(self):
        return self.settings.get("grandma_mode_enabled", True)

    def _get_user_tz(self):
        """
        Gets a timezone object for the user associated with the given message
        :param message: Message associated with request
        :return: timezone object
        """
        return gettz(self.location_timezone) if self.location_timezone else \
            default_timezone()

    def _set_easter_egg_events(self):
        self.event_scheduler.schedule_event(Message("christmas_day"), {
            "event": f"{self.skill_id}.christmas_day",
            "time": datetime(year=datetime.now().year, month=12, day=25, hour=8, tzinfo=self._get_user_tz()),
            "repeat": ANNUAL
        })

    def handle_christmas_day(self, _: Message):
        # Mark 1
        FallingDots(bus=self.bus).run()
        # GUI
        if self.gui:
            self.gui.show_text(ASCII_SNOW)
        self.speak("Ho ho ho")

    @intent_handler(IntentBuilder("grandma_mode_intent").require("grandma_mode_keyword").build())
    def handle_grandma_mode(self, _):
        self.settings["grandma_mode_enabled"] = True
        self.speak("Ok, we'll tone it down a bit.")

    @intent_handler(IntentBuilder("adult_mode_intent").require("adult_mode_keyword").build())
    def handle_adult_mode(self, _):
        self.settings["grandma_mode_enabled"] = False
        self.speak("Do you feel lucky, punk?")

    @intent_handler(IntentBuilder("stardate_intent").require("stardate_keyword").build())
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

    @intent_handler(IntentBuilder("pod_bay_doors_intent").require("pod_bay_doors_keyword").build())
    def handle_pod_intent(self, _):
        self.speak_dialog("pod")

    @intent_handler(
        IntentBuilder("robotics_laws_intent")
        .require("robotics_keyword")
        .require("law_keyword")
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
        IntentBuilder("rock_paper_scissors_lizard_spock_intent")
        .require("rock_paper_scissors_lizard_spock_keyword")
        .build()
    )
    def handle_rock_paper_scissors_lizard_spock_intent(self, _):
        self.speak_dialog("rock_paper_scissors_lizard_spock")

    @intent_handler(IntentBuilder("languages_you_speak_intent").require("languages_you_speak_keyword").build())
    def handle_number_of_languages_intent(self, _):
        self.speak_dialog("languages")

    @intent_handler(IntentBuilder("portal_intent").require("portal_keyword").build())
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

    @intent_handler(IntentBuilder("hal_intent").require("hal_keyword").build())
    def handle_hal_intent(self, _):
        path, files = self.get_reference_files("/sounds/hal", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(mp3)
        else:
            self.speak_dialog("bad_file")

    @intent_handler(IntentBuilder("duke_nukem_intent").require("duke_nukem_keyword").build())
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

    @intent_handler(IntentBuilder("arnold_intent").require("arnold_keyword").build())
    def handle_arnold_intent(self, _):
        path, files = self.get_reference_files("/sounds/arnold", "wav")
        if len(files):
            wav = path + "/" + random.choice(files)
            self.play_audio(wav)
        else:
            self.speak_dialog("bad_file")

    @intent_handler(IntentBuilder("bender_intent").require("bender_keyword").build())
    def handle_bender_intent(self, _):
        path, files = self.get_reference_files("/sounds/bender", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(mp3)
        else:
            self.speak_dialog("bad_file")

    @intent_handler(IntentBuilder("glados_intent").require("glados_keyword").build())
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
