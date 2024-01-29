# Pytest boilerplate
from genericpath import isdir
from json import dumps
from os.path import dirname, join
from os import environ, getenv, makedirs
from unittest.mock import Mock, patch
import shutil

from ovos_plugin_manager.skills import find_skill_plugins
from ovos_utils.messagebus import FakeBus
import pytest

from skill_easter_eggs import EasterEggsSkill
from skill_easter_eggs.constants import SPICY_SOUNDS


@pytest.fixture(scope="session")
def test_skill(test_skill_id="skill-easter-eggs.openvoiceos", bus=FakeBus()):
    # Get test skill
    bus.emitter = bus.ee
    bus.run_forever()
    skill_entrypoint = getenv("TEST_SKILL_ENTRYPOINT")
    if not skill_entrypoint:
        skill_entrypoints = list(find_skill_plugins().keys())
        assert test_skill_id in skill_entrypoints
        skill_entrypoint = test_skill_id

    skill = EasterEggsSkill(skill_id=test_skill_id, bus=bus)
    skill.speak = Mock()
    skill.speak_dialog = Mock()
    skill.play_audio = Mock()
    yield skill
    shutil.rmtree(join(dirname(__file__), "skill_fs"), ignore_errors=False)


@pytest.fixture(scope="function")
def reset_skill_mocks(test_skill):
    # Reset mocks before each test
    test_skill.speak.reset_mock()
    test_skill.speak_dialog.reset_mock()
    test_skill.play_audio.reset_mock()


class TestEasterEggSkill:
    test_fs = join(dirname(__file__), "skill_fs")
    data_dir = join(test_fs, "data")
    conf_dir = join(test_fs, "config")
    environ["XDG_DATA_HOME"] = data_dir
    environ["XDG_CONFIG_HOME"] = conf_dir
    if not isdir(test_fs):
        makedirs(data_dir)
        makedirs(conf_dir)

    with open(join(conf_dir, "mycroft.conf"), "w", encoding="utf-8") as f:
        f.write(dumps({"Audio": {"backends": {"ocp": {"active": True}}}}))

    def test_grandma_mode_set_by_default(self, test_skill):
        assert test_skill.grandma_mode is True

    def test_ocp_api_available(self, test_skill):
        assert test_skill.ocp is not None

    def test_ocp_api_unavailable_when_ocp_is_disabled(self, test_skill):
        # TODO: Fully implement
        assert True

    def test_handle_grandma_mode(self, test_skill):
        test_skill.handle_grandma_mode(None)
        test_skill.speak.assert_called_once_with("Ok, we'll tone it down a bit.")
        assert test_skill.settings["grandma_mode_enabled"] is True

    def test_handle_adult_mode(self, test_skill):
        # TODO: Fully implement
        assert True

    def test_handle_stardate_intent(self, test_skill, reset_skill_mocks):
        test_skill.handle_stardate_intent(None)
        test_skill.speak_dialog.assert_called_once_with(
            "stardate", {"stardate": test_skill._create_spoken_stardate()}
        )

    def test_create_spoken_stardate(self, test_skill):
        # TODO: Fully implement
        assert True

    def test_handle_pod_intent(self, test_skill, reset_skill_mocks):
        # TODO: Fully implement
        assert True

    def test_handle_robotic_laws_intent(self, test_skill, reset_skill_mocks):
        # TODO: Fully implement
        assert True

    def test_handle_rock_paper_scissors_lizard_spock_intent(self, test_skill, reset_skill_mocks):
        # TODO: Fully implement
        assert True

    def test_handle_number_of_languages_intent(self, test_skill, reset_skill_mocks):
        # TODO: Fully implement
        assert True

    def test_handle_portal_intent(self, test_skill, reset_skill_mocks):
        with patch("skill_easter_eggs.EasterEggsSkill._play_in_ocp") as mock_ocp_play:
            test_skill.handle_portal_intent(None)
            mock_ocp_play.assert_called_once()

    def test_get_reference_files_grandma_mode(self, test_skill):
        spicy_arnold_sounds = [
                gubernator.replace("sounds/arnold/", "")
                for gubernator in SPICY_SOUNDS
                if gubernator.startswith("sounds/arnold")
            ]
        with patch("skill_easter_eggs.EasterEggsSkill.grandma_mode", True):
            _, arnold_safe = test_skill.get_reference_files(
                "/sounds/arnold", extension="wav"
            )
            for spicy_arnold in spicy_arnold_sounds:
                assert spicy_arnold not in arnold_safe
        with patch("skill_easter_eggs.EasterEggsSkill.grandma_mode", False):
            _, arnold_spicy = test_skill.get_reference_files(
                "sounds/arnold", extension="wav"
            )
            for spicy_arnold in  [
                gubernator.replace("sounds/arnold/", "")
                for gubernator in SPICY_SOUNDS
                if gubernator.startswith("sounds/arnold")
            ]:
                assert spicy_arnold in arnold_spicy

    def test_handle_hal_intent(self, test_skill, reset_skill_mocks):
        # TODO: Fully implement
        assert True

    def test_handle_dukenukem_intent(self, test_skill, reset_skill_mocks):
        # TODO: Fully implement
        assert True

    def test_handle_handle_arnold_intent(self, test_skill, reset_skill_mocks):
        # TODO: Fully implement
        assert True

    def test_handle_bender_intent(self, test_skill, reset_skill_mocks):
        # TODO: Fully implement
        assert True

    def test_handle_glados_intent(self, test_skill, reset_skill_mocks):
        # TODO: Fully implement
        assert True

    def test_handle_conan_intent(self, test_skill, reset_skill_mocks):
        test_skill.handle_conan_intent(None)
        test_skill.play_audio.assert_called_once()
        assert "skill_easter_eggs/sounds/conan/" in test_skill.play_audio.call_args.kwargs.get("filename", "")
        assert test_skill.speak_dialog.called is False

    def test_handle_bill_and_ted_intent(self, test_skill, reset_skill_mocks):
        test_skill.handle_bill_and_ted_intent(None)
        test_skill.play_audio.assert_called_once()
        assert "skill_easter_eggs/sounds/billandted/" in test_skill.play_audio.call_args.kwargs.get("filename", "")
        assert test_skill.speak_dialog.called is False

    def test_handle_malibu_stacey_intent(self, test_skill, reset_skill_mocks):
        test_skill.handle_malibu_stacey_intent(None)
        test_skill.play_audio.assert_called_once()
        assert "skill_easter_eggs/sounds/malibustacey/" in test_skill.play_audio.call_args.kwargs.get("filename", "")
        assert test_skill.speak_dialog.called is False

    def test_get_display_date(self, test_skill):
        # TODO: Fully implement
        assert True

    def test_play_in_ocp(self, test_skill):
        with open(join(self.conf_dir, "mycroft.conf"), "w", encoding="utf-8") as f:
            f.write(dumps({"Audio": {"backends": {"ocp": {"active": True}}}}))
        media_path = "~/sounds/test.mp3"

        with patch("ovos_bus_client.apis.ocp.OCPInterface.play") as mock_ocp_play:
            test_skill._play_in_ocp(media_path)
            mock_ocp_play.assert_called_once_with(
                tracks=[
                    {
                        "match_confidence": 100,
                        "media_type": 1,
                        "length": 0,
                        "uri": media_path,
                        "playback": 2,
                        "image": "",
                        "bg_image": "",
                        "skill_icon": "",
                        "title": "Easter Egg!",
                        "skill_id": test_skill.skill_id,
                    }
                ]
            )

    def test_play_in_ocp_custom_title(self, test_skill):
        media_path = "~/sounds/test.mp3"
        test_skill.ocp = Mock()
        test_skill._play_in_ocp(media=media_path, title="GladOS says...")
        test_skill.ocp.play.assert_called_once_with(
            tracks=[
                {
                    "match_confidence": 100,
                    "media_type": 1,
                    "length": 0,
                    "uri": media_path,
                    "playback": 2,
                    "image": "",
                    "bg_image": "",
                    "skill_icon": "",
                    "title": "GladOS says...",
                    "skill_id": test_skill.skill_id,
                }
            ]
        )


if __name__ == "__main__":
    pytest.main()
