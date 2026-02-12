import os
import json
import wave
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl, QObject, QTimer
from .LogManager import LogManager
from .CaminhoPersistenteUtils import obter_caminho_persistente
from .ApplicationPathUtils import get_app_base_path
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

        self._sound_base_dir = self._find_sound_directory()
        
        self._sound_filenames = [
            "mixkit-alarm-clock-beep-988.wav",
            "mixkit-alarm-digital-clock-beep-989.wav",
            "mixkit-alarm-tone-996.wav",
            "mixkit-alert-alarm-1005.wav",
            "mixkit-battleship-alarm-1001.wav",
            "mixkit-casino-jackpot-alarm-and-coins-1991.wav",
            "mixkit-casino-win-alarm-and-coins-1990.wav",
            "mixkit-city-alert-siren-loop-1008.wav",
            "mixkit-classic-alarm-995.wav",
            "mixkit-classic-short-alarm-993.wav",
            "mixkit-classic-winner-alarm-1997.wav",
            "mixkit-critical-alarm-1004.wav",
            "mixkit-data-scaner-2847.wav",
            "mixkit-digital-clock-digital-alarm-buzzer-992.wav",
            "mixkit-emergency-alert-alarm-1007.wav",
            "mixkit-facility-alarm-908.wav",
            "mixkit-facility-alarm-sound-999.wav",
            "mixkit-game-notification-wave-alarm-987.wav",
            "mixkit-interface-hint-notification-911.wav",
            "mixkit-morning-clock-alarm-1003.wav",
            "mixkit-retro-game-emergency-alarm-1000.wav",
            "mixkit-rooster-crowing-in-the-morning-2462.wav",
            "mixkit-scanning-sci-fi-alarm-905.wav",
            "mixkit-security-facility-breach-alarm-994.wav",
            "mixkit-short-rooster-crowing-2470.wav",
            "mixkit-slot-machine-payout-alarm-1996.wav",
            "mixkit-slot-machine-win-alarm-1995.wav",
            "mixkit-sound-alert-in-hall-1006.wav",
            "mixkit-spaceship-alarm-998.wav",
            "mixkit-space-shooter-alarm-1002.wav",
            "mixkit-street-public-alarm-997.wav",
            "mixkit-vintage-warning-alarm-990.wav",
            "mixkit-warning-alarm-buzzer-991.wav"
        ]

        self._sounds = []
        if self._sound_base_dir:
            for filename in self._sound_filenames:
                full_path = os.path.join(self._sound_base_dir, filename)
                self._sounds.append(os.path.normpath(full_path))

        else:
            logger.error("Diretório de sons 'assets/sound' não foi encontrado.")

        self._load_config()

    def _find_sound_directory(self):
        try:
            base = get_app_base_path() or os.path.dirname(os.path.abspath(__file__))

        except Exception:
            base = os.path.dirname(os.path.abspath(__file__))

        candidates = [
            os.path.join(base, 'source', 'assets', 'sound'),
            os.path.join(base, 'assets', 'sound'),
            os.path.join(base, '_internal', 'assets', 'sound'),
            os.path.join(base, '_internal', 'sound'),
            os.path.join(os.path.dirname(base), 'assets', 'sound'),
            os.path.join(base, 'main.dist', 'assets', 'sound'),
            os.path.join(base, 'dist', 'main.dist', 'assets', 'sound'),
        ]

        current_dir = os.path.dirname(os.path.abspath(__file__))
        candidates.extend([
            os.path.join(current_dir, '..', 'assets', 'sound'),
            os.path.join(current_dir, 'assets', 'sound'),
            os.path.join(current_dir, '..', '..', 'assets', 'sound'),
        ])

        for path in candidates:
            abs_path = os.path.abspath(path)
            if os.path.isdir(abs_path):
                return abs_path

        try:
            max_depth = 3
            for root, dirs, files in os.walk(base):
                rel = os.path.relpath(root, base)
                if rel == '.':
                    depth = 0

                else:
                    depth = rel.count(os.sep) + 1

                if depth > max_depth:
                    dirs[:] = []
                    continue

                lower_root = root.replace('\\\\', '/').lower()
                if '/assets/' in lower_root and lower_root.endswith('/sound'):
                    return os.path.abspath(root)

            for root, dirs, files in os.walk(base):
                for d in dirs:
                    if d.lower() == 'sound' and 'assets' in os.path.dirname(os.path.join(root, d)).lower():
                        return os.path.abspath(os.path.join(root, d))

        except Exception as e:
            logger.warning(f"Erro ao procurar diretório de sons: {e}")

        return ""

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
                    logger.warning(f"Caminho salvo não encontrado (projeto movido?): {sound_path}. Usando padrão.")
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
        return os.path.basename(path)

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
