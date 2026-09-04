# pylint: disable=unused-import,missing-docstring,invalid-name
import random
from datetime import datetime
from os import getenv, listdir
from os.path import dirname, join

from dateutil.tz import gettz
from ovos_bus_client.apis.ocp import OCPInterface
from ovos_bus_client.message import Message
from ovos_config.locale import get_default_tz
from ovos_mark1.faceplate.animations import FallingDots
from ovos_number_parser import extract_number
from ovos_workshop.decorators import intent_handler, skill_api_method
from ovos_workshop.skills import OVOSSkill
from skill_easter_eggs.constants import ANNUAL, ASCII_SNOW, SPICY_SOUNDS
from skill_easter_eggs.stardate import StarDate


class EasterEggsSkill(OVOSSkill):
    def initialize(self):
        self.ocp = OCPInterface(
            bus=self.bus
        )  # pylint: disable=attribute-defined-outside-init
        self.bus.on(f"{self.skill_id}.christmas_day", self.handle_christmas_day)
        self._set_easter_egg_events()

    @property
    def grandma_mode(self):
        return self.settings.get("grandma_mode_enabled", True)

    def _get_user_tz(self):
        """
        Gets a timezone object for the user associated with the given message
        :param message: Message associated with request
        :return: timezone object
        """
        return (
            gettz(self.location_timezone)
            if self.location_timezone
            else get_default_tz()
        )

    def _set_easter_egg_events(self):
        self.event_scheduler.schedule_repeating_event(
            self.handle_christmas_day,
            datetime(
                year=datetime.now().year,
                month=12,
                day=25,
                hour=8,
                tzinfo=self._get_user_tz(),
            ).timestamp(),
            ANNUAL,
            {},
            "Christmas Day",
            {
                "skill_id": self.skill_id,
                "event": f"{self.skill_id}.christmas_day",
                "time": datetime(
                    year=datetime.now().year,
                    month=12,
                    day=25,
                    hour=8,
                    tzinfo=self._get_user_tz(),
                ).timestamp(),
                "repeat": ANNUAL,
            },
        )

    def handle_christmas_day(self, _: Message):
        # Mark 1
        FallingDots(bus=self.bus).run()
        # GUI
        if self.gui:
            self.gui.show_text(ASCII_SNOW)
        self.speak_dialog("santa")

    @intent_handler("grandma_mode_intent.intent")
    def handle_grandma_mode(self, _):
        self.settings["grandma_mode_enabled"] = True
        self.speak("Ok, we'll tone it down a bit.")

    @intent_handler("adult_mode_intent.intent")
    def handle_adult_mode(self, _):
        self.settings["grandma_mode_enabled"] = False
        self.speak("Do you feel lucky, punk?")

    @intent_handler("stardate_intent.intent")
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

    @intent_handler("pod_bay_doors_intent.intent")
    def handle_pod_intent(self, _):
        self.speak_dialog("pod")

    @intent_handler("law_of_robotics.intent")
    def handle_robotic_laws_intent(self, message: Message):
        law = str(message.data.get("ordinal", ""))
        law = extract_number(law, ordinals=True, lang=self.lang)
        self.log.debug("law: %s", law)
        if not law:
            self.log.debug("No specific law detected, reciting all three")
            self.speak_dialog("rule1")
            self.speak_dialog("rule2")
            self.speak_dialog("rule3")
            return
        # lingua-franca currently returns a number, but let's not trust, let's ensure
        law = str(law)
        if law == "1":
            self.log.debug("First law of robotics requested")
            self.speak_dialog("rule1")
        elif law == "2":
            self.log.debug("Second law of robotics requested")
            self.speak_dialog("rule2")
        elif law == "3":
            self.log.debug("Third law of robotics requested")
            self.speak_dialog("rule3")
        else:
            self.log.debug("Invalid law requested")
            self.speak_dialog("invalid_law")

    @intent_handler("rock_paper_scissors_lizard_spock_intent.intent")
    def handle_rock_paper_scissors_lizard_spock_intent(self, _):
        self.speak_dialog("rock_paper_scissors_lizard_spock")

    @intent_handler("languages_you_speak_intent.intent")
    def handle_number_of_languages_intent(self, _):
        self.speak_dialog("languages")

    @intent_handler("portal_intent.intent")
    def handle_portal_intent(self, _):
        path, files = self.get_reference_files("sounds/portal", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self._play_in_ocp(mp3, title="Portal Easter Egg")
        else:
            self.speak_dialog("bad_file")

    def get_reference_files(self, path_ending: str, extension: str):
        """Get a list of files in a directory

        If grandma mode is enabled, filter out spicy sounds
        path_ending: str, path to directory, should not start with /
        extension: str, file extension to filter by
        """
        path_ending = path_ending.strip("/")
        path = join(dirname(__file__), path_ending)
        if self.grandma_mode:
            files = [
                sound
                for sound in listdir(path)
                if f".{extension}" in sound
                and f"{path_ending}/{sound}" not in SPICY_SOUNDS
            ]
        else:
            files = [sound for sound in listdir(path) if f".{extension}" in sound]
        return path, files

    @intent_handler("hal_intent.intent")
    def handle_hal_intent(self, _):
        path, files = self.get_reference_files("sounds/hal", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(mp3)
        else:
            self.speak_dialog("bad_file")

    @intent_handler("duke_nukem_intent.intent")
    def handle_dukenukem_intent(self, _):
        if not self.grandma_mode:
            path, files = self.get_reference_files("sounds/dukenukem", "wav")
            if len(files):
                wav = path + "/" + random.choice(files)
                self.play_audio(wav)
            else:
                self.speak_dialog("bad_file")
        else:
            self.speak("Duke Who-Kem?")

    @intent_handler("arnold_intent.intent")
    def handle_arnold_intent(self, _):
        path, files = self.get_reference_files("sounds/arnold", "wav")
        if len(files):
            wav = path + "/" + random.choice(files)
            self.play_audio(wav)
        else:
            self.speak_dialog("bad_file")

    @intent_handler("bender_intent.intent")
    def handle_bender_intent(self, _):
        path, files = self.get_reference_files("sounds/bender", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(mp3)
        else:
            self.speak_dialog("bad_file")

    @intent_handler("glados_intent.intent")
    def handle_glados_intent(self, _):
        path, files = self.get_reference_files("sounds/glados", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self._play_in_ocp(mp3, title="GlaDOS says...")
        else:
            self.speak_dialog("bad_file")

    @intent_handler("conan_intent.intent")
    def handle_conan_intent(self, _):
        path, files = self.get_reference_files("sounds/conan", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(filename=mp3)
        else:
            self.speak_dialog("bad_file")

    @intent_handler("bill_and_ted_intent.intent")
    def handle_bill_and_ted_intent(self, _):
        path, files = self.get_reference_files("sounds/billandted", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(filename=mp3)
        else:
            self.speak_dialog("bad_file")

    @intent_handler("malibu_stacey_intent.intent")
    def handle_malibu_stacey_intent(self, _):
        path, files = self.get_reference_files("sounds/malibustacey", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(filename=mp3)
        else:
            self.speak_dialog("bad_file")

    @intent_handler("sing_intent.intent")
    def handle_sing_intent(self, _):
        if not self._sounds_like_popey():
            confirm = self.ask_yesno("too_shy")
            if confirm == "no":
                return
        self.speak_dialog("singing", wait=5)
        path, files = self.get_reference_files("sounds/sing", "mp3")
        if len(files):
            mp3 = path + "/" + random.choice(files)
            self.play_audio(filename=mp3)
        else:
            self.speak_dialog("bad_file")

    def _sounds_like_popey(self):
        tts = self.config_core.get("tts", {})
        if "mimic" in tts.get("module", "").lower():
            return True
        # Default ovos-tts-plugin-server voice, Alan Pope
        if tts.get("module") == "ovos-tts-plugin-server" and not tts.get(
            "ovos-tts-plugin-server"
        ):
            return True
        for k, v in tts.items():
            if isinstance(v, dict):
                if "alan" in v.get("voice", "") and tts.get("module", "") == k:
                    return True
                if "ap" in v.get("voice", "") and tts.get("module", "") == k:
                    return True
                if "alan" in v.get("model", "") and tts.get("module", "") == k:
                    return True
        return False

    def _sounds_like_sam(self) -> bool:
        tts = self.config_core.get("tts", {})
        if "sam" in tts.get("module", "").lower():
            return True
        return False

    @skill_api_method
    def get_display_date(self):
        return StarDate().getStardate()

    def _play_in_ocp(self, media, title="Easter Egg!"):
        data = {
            "match_confidence": 100,
            "media_type": 1,  # MediaType.AUDIO
            "length": 0,
            "uri": media,
            "playback": 2,  # PlaybackType.AUDIO
            "image": "",
            "bg_image": "",
            "skill_icon": "",
            "title": title,
            "skill_id": self.skill_id,
        }
        if getenv("IS_OVOS_CONTAINER"):
            data["uri"] = (
                f"https://github.com/OpenVoiceOS/ovos-skill-easter-eggs/raw/dev/sounds/{'/'.join(media.split('/')[-2:])}"
            )
        self.ocp.play(tracks=[data])
