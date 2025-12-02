import os
import json
import wave
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl, QObject, QTimer
from .LogManager import LogManager
from .CaminhoPersistenteUtils import obter_caminho_persistente

logger = LogManager.get_logger()


class SoundManager(QObject):
    _instance = None
    CONFIG_FILE = "sound_config.json"

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = SoundManager()

        return cls._instance

    def __init__(self):
        super().__init__()
        self._effect = QSoundEffect()
        self._effect.setVolume(0.9)
        self._current_path = ""
        self._audio_duration_ms = 3000
        self._alarm_interval = 5

        self._repeat_timer = QTimer()
        self._repeat_timer.timeout.connect(self._on_repeat_timeout)
        self._is_repeating = False

        self._sounds = [
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-critical-alarm-1004.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-data-scaner-2847.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-digital-clock-digital-alarm-buzzer-992.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-emergency-alert-alarm-1007.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-facility-alarm-908.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-facility-alarm-sound-999.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-game-notification-wave-alarm-987.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-interface-hint-notification-911.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-morning-clock-alarm-1003.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-retro-game-emergency-alarm-1000.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-rooster-crowing-in-the-morning-2462.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-scanning-sci-fi-alarm-905.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-security-facility-breach-alarm-994.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-short-rooster-crowing-2470.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-slot-machine-payout-alarm-1996.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-slot-machine-win-alarm-1995.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-sound-alert-in-hall-1006.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-spaceship-alarm-998.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-space-shooter-alarm-1002.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-street-public-alarm-997.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-vintage-warning-alarm-990.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-warning-alarm-buzzer-991.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-alarm-clock-beep-988.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-alarm-digital-clock-beep-989.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-alarm-tone-996.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-alert-alarm-1005.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-battleship-alarm-1001.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-casino-jackpot-alarm-and-coins-1991.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-casino-win-alarm-and-coins-1990.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-city-alert-siren-loop-1008.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-classic-alarm-995.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-classic-short-alarm-993.wav",
            r"C:\Users\ferna\DEV\Python\Lumen\source\assets\sound\mixkit-classic-winner-alarm-1997.wav",
        ]

        self._load_config()

    def _get_config_path(self):
        config_dir = obter_caminho_persistente()
        return os.path.join(config_dir, self.CONFIG_FILE)

    def _load_config(self):
        config_path = self._get_config_path()
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                sound_path = config.get("sound_path", "")
                if sound_path and os.path.exists(sound_path):
                    self._current_path = sound_path

                else:
                    self._current_path = self._sounds[0] if self._sounds else ""

                self._alarm_interval = config.get("alarm_interval", 5)
                logger.info(f"Configurações de som carregadas: {config_path}")

            else:
                self._current_path = self._sounds[0] if self._sounds else ""
                self._alarm_interval = 5
                self._save_config()
                logger.info(f"Arquivo de configuração criado com valores padrão: {config_path}")

        except Exception as e:
            logger.error(f"Erro ao carregar configurações de som: {e}")
            self._current_path = self._sounds[0] if self._sounds else ""
            self._alarm_interval = 5

        self._audio_duration_ms = self._get_wav_duration_ms(self._current_path)

    def _save_config(self):
        config_path = self._get_config_path()

        try:
            config = {
                "sound_path": self._current_path,
                "alarm_interval": self._alarm_interval
            }

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)

            logger.info(f"Configurações de som salvas: {config_path}")

        except Exception as e:
            logger.error(f"Erro ao salvar configurações de som: {e}")

    def _get_wav_duration_ms(self, path):
        if not path or not os.path.exists(path):
            return 3000

        try:
            with wave.open(path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration_seconds = frames / float(rate)
                duration_ms = int(duration_seconds * 1000)
                logger.debug(f"Duração do WAV '{os.path.basename(path)}': {duration_ms}ms ({duration_seconds:.2f}s)")
                return duration_ms

        except Exception as e:
            logger.warning(f"Erro ao obter duração do WAV '{path}': {e}")
            return 3000

    def get_audio_duration_ms(self):
        return self._audio_duration_ms

    def get_available_sounds(self):
        return [p for p in self._sounds if p and isinstance(p, str)]

    def get_sound_display_name(self, path):
        return path.replace("\\", "/").split("/")[-1]

    def get_current_sound(self):
        return self._current_path

    def set_sound(self, path):
        if path and os.path.exists(path):
            self._current_path = path
            self._audio_duration_ms = self._get_wav_duration_ms(path)
            self._save_config()

    def get_alarm_interval(self):
        return self._alarm_interval

    def set_alarm_interval(self, seconds):
        self._alarm_interval = seconds
        self._save_config()

    def _prepare_effect(self):
        try:
            self._effect.stop()

        except Exception as e:
            logger.error(f"Error stopping sound effect: {e}")

        self._effect = QSoundEffect()
        self._effect.setVolume(0.9)

        if self._current_path and os.path.exists(self._current_path):
            self._effect.setSource(QUrl.fromLocalFile(self._current_path))

    def _on_repeat_timeout(self):
        if not self._is_repeating:
            return

        logger.debug("Repetindo alarme...")
        self._prepare_effect()
        self._effect.setLoopCount(1)
        self._effect.play()

        self._schedule_next_repeat()

    def _schedule_next_repeat(self):
        audio_duration = self._audio_duration_ms
        interval_ms = self._alarm_interval * 1000
        total_delay = audio_duration + interval_ms

        logger.debug(
            f"Próxima repetição em: {total_delay}ms "
            f"(áudio: {audio_duration}ms + intervalo: {interval_ms}ms)"
        )
        self._repeat_timer.start(total_delay)

    def play(self):
        self._prepare_effect()
        self._effect.setLoopCount(1)
        self._effect.play()

    def play_repeating(self):
        self._is_repeating = True

        if self._current_path:
            self._audio_duration_ms = self._get_wav_duration_ms(self._current_path)

        logger.debug(
            f"Iniciando alarme repetitivo - Duração: {self._audio_duration_ms}ms, "
            f"Intervalo: {self._alarm_interval}s"
        )

        self._prepare_effect()
        self._effect.setLoopCount(1)
        self._effect.play()

        self._schedule_next_repeat()

    def play_looping(self):
        self.play_repeating()

    def stop(self):
        try:
            self._is_repeating = False
            self._repeat_timer.stop()
            self._effect.stop()
            self._effect.setLoopCount(1)
            logger.debug("Alarme parado.")

        except Exception as e:
            logger.error(f"Error stopping sound effect: {e}")

    def preview(self, path):
        if path and os.path.exists(path):
            try:
                self._is_repeating = False
                self._repeat_timer.stop()
                self._effect.stop()

            except Exception as e:
                logger.error(f"Error stopping sound effect: {e}")

            self._effect = QSoundEffect()
            self._effect.setVolume(0.9)
            self._effect.setSource(QUrl.fromLocalFile(path))
            self._effect.setLoopCount(1)
            self._effect.play()

    def get_duration_for_path(self, path):
        return self._get_wav_duration_ms(path)
