from __future__ import annotations

import json
import os
import queue
import threading
import time
from pathlib import Path

from PySide6.QtCore import QObject, Signal

try:
    import sounddevice as sounddevice
    from vosk import KaldiRecognizer, Model, SetLogLevel
except ImportError:
    sounddevice = None
    KaldiRecognizer = None
    Model = None
    SetLogLevel = None


class VoiceEngine(QObject):
    listening_changed = Signal(bool, str)
    transcript_ready = Signal(str)
    status_changed = Signal(str)
    error = Signal(str)

    def __init__(self, model_path: str | Path | None = None, wake_word: str = "bolt") -> None:
        super().__init__()
        project_root = Path(__file__).resolve().parent.parent
        default_path = project_root / "models" / "vosk-model-small-en-us-0.15"
        self.model_path = Path(model_path or os.getenv("BOLT_VOICE_MODEL", default_path))
        self.wake_word = wake_word.lower()
        self.wake_phrases = (
            f"hey {self.wake_word}",
            f"ok {self.wake_word}",
            self.wake_word,
            "hey volt",
            "ok volt",
            "volt",
            "hey bold",
            "ok bold",
            "bold",
        )
        self._audio_queue: queue.Queue[bytes] = queue.Queue(maxsize=24)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="bolt-voice", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._thread = None

    def _run(self) -> None:
        if sounddevice is None or Model is None or KaldiRecognizer is None:
            self.error.emit("Install the local voice packages before enabling Bolt voice control.")
            return
        if not self.model_path.exists():
            self.error.emit(f"Voice model not found: {self.model_path}")
            return
        failed = False
        try:
            if SetLogLevel is not None:
                SetLogLevel(-1)
            model = Model(str(self.model_path))
            self._clear_audio_queue()
            last_error: Exception | None = None
            for device in self._device_candidates():
                for sample_rate in self._sample_rates(device):
                    if self._stop_event.is_set():
                        return
                    try:
                        stream_options = {
                            "device": device,
                            "samplerate": sample_rate,
                            "blocksize": 1600,
                            "dtype": "int16",
                            "channels": 1,
                            "callback": self._audio_callback,
                        }
                        with sounddevice.RawInputStream(**stream_options) as stream:
                            self._listen(model, stream)
                        return
                    except Exception as exc:
                        last_error = exc
            if last_error is not None:
                raise last_error
        except Exception as exc:
            failed = True
            self.error.emit(str(exc) or "Bolt could not access the microphone.")
        finally:
            self.listening_changed.emit(False, "Standby")
            if not failed:
                self.status_changed.emit("Say Bolt to wake me")

    def _clear_audio_queue(self) -> None:
        while True:
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                return

    def _device_candidates(self) -> list[int | str | None]:
        configured = os.getenv("BOLT_VOICE_DEVICE", "").strip()
        if configured:
            try:
                return [int(configured)]
            except ValueError:
                return [configured]
        devices = sounddevice.query_devices()
        host_apis = sounddevice.query_hostapis()
        ranked: list[tuple[int, int]] = []
        for index, device in enumerate(devices):
            if int(device.get("max_input_channels", 0)) < 1:
                continue
            name = str(device.get("name", "")).lower()
            host_api_index = int(device.get("hostapi", -1))
            host_api = ""
            if 0 <= host_api_index < len(host_apis):
                host_api = str(host_apis[host_api_index].get("name", "")).lower()
            host_rank = 0 if "wasapi" in host_api else 1 if "directsound" in host_api else 2
            name_rank = 0 if "microphone array" in name else 1 if "microphone" in name else 2
            ranked.append((host_rank * 10 + name_rank, index))
        ranked.sort()
        return [index for _, index in ranked] or [None]

    def _select_device(self) -> int | str | None:
        return self._device_candidates()[0]

    def _device_sample_rate(self, device: int | str | None) -> float | None:
        try:
            details = sounddevice.query_devices(device, "input")
            value = float(details.get("default_samplerate", 0))
            return value or None
        except Exception:
            return None

    def _sample_rates(self, device: int | str | None) -> list[float]:
        native_rate = self._device_sample_rate(device)
        rates = [16000.0]
        if native_rate and native_rate not in rates:
            rates.append(native_rate)
        return rates

    def _listen(self, model: object, stream: object) -> None:
        grammar = json.dumps([*self.wake_phrases, "[unk]"])
        recognizer = KaldiRecognizer(model, stream.samplerate, grammar)
        active = False
        phrase_parts: list[str] = []
        last_speech = 0.0
        self.status_changed.emit("Say Bolt to wake me")
        while not self._stop_event.is_set():
            try:
                data = self._audio_queue.get(timeout=0.2)
            except queue.Empty:
                if active and phrase_parts and time.monotonic() - last_speech > 1.25:
                    self._finish_phrase(phrase_parts)
                    active = False
                    phrase_parts = []
                    recognizer = KaldiRecognizer(model, stream.samplerate, grammar)
                continue
            accepted = recognizer.AcceptWaveform(data)
            result = json.loads(recognizer.Result() if accepted else recognizer.PartialResult())
            text = str(result.get("text" if accepted else "partial", "")).strip().lower()
            if not text:
                if active and phrase_parts and time.monotonic() - last_speech > 1.25:
                    self._finish_phrase(phrase_parts)
                    active = False
                    phrase_parts = []
                    recognizer = KaldiRecognizer(model, stream.samplerate, grammar)
                continue
            last_speech = time.monotonic()
            if not active:
                matched_phrase = next((phrase for phrase in self.wake_phrases if phrase in text), None)
                if matched_phrase is None:
                    continue
                phrase = text.split(matched_phrase, 1)[1].strip()
                active = True
                phrase_parts = [phrase] if phrase else []
                self.listening_changed.emit(True, "Listening")
                self.status_changed.emit("Listening for your question")
                recognizer = KaldiRecognizer(model, stream.samplerate)
                continue
            if accepted:
                phrase_parts.append(text)
            if time.monotonic() - last_speech > 1.25 and phrase_parts:
                self._finish_phrase(phrase_parts)
                active = False
                phrase_parts = []
                recognizer = KaldiRecognizer(model, stream.samplerate, grammar)

    def _audio_callback(self, indata: object, frames: int, timing: object, status: object) -> None:
        del frames, timing, status
        try:
            self._audio_queue.put_nowait(bytes(indata))
        except queue.Full:
            return

    def _finish_phrase(self, phrase_parts: list[str]) -> None:
        phrase = " ".join(part for part in phrase_parts if part).strip()
        if phrase:
            self.listening_changed.emit(False, "Sending")
            self.transcript_ready.emit(phrase)
