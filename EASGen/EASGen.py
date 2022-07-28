from pydub import AudioSegment
from pydub.generators import Sine


class EASGen:
    """Generate various EAS Alert Types."""

    _silence = AudioSegment.silent()

    @classmethod
    def _mark(cls, sample_rate: int = 24000) -> AudioSegment:
        return Sine(2083.3, sample_rate=sample_rate, bit_depth=16).to_audio_segment(
            duration=float(1000 / 520.83), volume=-3
        )

    @classmethod
    def _space(cls, sample_rate: int = 24000) -> AudioSegment:
        return Sine(1562.5, sample_rate=sample_rate, bit_depth=16).to_audio_segment(
            duration=float(1000 / 520.83), volume=-3
        )

    @classmethod
    def _attn(cls, mode: str = "", sample_rate: int = 24000):
        if mode == "NWS":
            return Sine(1050, sample_rate=sample_rate, bit_depth=16).to_audio_segment(
                duration=9000, volume=-4
            )
        elif mode == "BROADCASTER":
            return Sine(1050, sample_rate=44100, bit_depth=16).to_audio_segment(
                duration=9000, volume=-4
            )
        else:
            return (
                Sine(853, sample_rate=sample_rate, bit_depth=16)
                .to_audio_segment(duration=8000, volume=-10)
                .overlay(
                    Sine(960, sample_rate=sample_rate, bit_depth=16).to_audio_segment(
                        duration=8000, volume=-10
                    )
                )
            )

    @classmethod
    def _eom(cls, mode: str = "", sample_rate: int = 24000):
        eom = AudioSegment.empty()
        eoms = AudioSegment.empty()
        if mode == "NWS":
            for bit in "".join(
                format(ord(x), "08b")[::-1]
                for x in ("\xab" * 16) + "NNNN" + ("\x00" * 2)
            ):
                eom += cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
            eoms = (cls._silence + eom) * 3
        elif mode == "DIGITAL":
            for bit in "".join(
                format(ord(x), "08b")[::-1]
                for x in "\x00" + ("\xab" * 16) + "NNNN" + ("\xff" * 3)
            ):
                eom += cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
            data = cls._silence + eom
            eom = AudioSegment.empty()
            for bit in "".join(
                format(ord(x), "08b")[::-1]
                for x in ("\xab" * 16) + "NNNN" + ("\xff" * 3)
            ):
                eom += cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
            data += (cls._silence + eom) * 2
            eoms = data
        elif mode == "SAGE":
            for bit in "".join(
                format(ord(x), "08b")[::-1] for x in ("\xab" * 16) + "NNNN\xff"
            ):
                eom += cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
            eoms = (cls._silence + eom) * 3
        elif mode == "TRILITHIC":
            for bit in "".join(
                format(ord(x), "08b")[::-1] for x in ("\xab" * 16) + "NNNN"
            ):
                eom += cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
            eoms = (cls._silence[:850] + eom) * 3
        elif mode == "BROADCASTER":
            for bit in "".join(
                format(ord(x), "08b")[::-1]
                for x in ("\xab" * 16) + "NNNN" + ("\x00" * 3)
            ):
                eom += cls._space(44100) if bit == "0" else cls._mark(44100)
            eoms = (cls._silence + eom) * 3
        else:
            for bit in "".join(
                format(ord(x), "08b")[::-1] for x in ("\xab" * 16) + "NNNN"
            ):
                eom += cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
            eoms = (cls._silence + eom) * 3
        return eoms

    @classmethod
    def _header(cls, header_data: str, mode: str = "", sample_rate: int = 24000):
        header = AudioSegment.empty()
        headers = AudioSegment.empty()
        if mode == "NWS":
            data = ("\xab" * 16) + header_data + ("\x00" * 2)
            for bit in "".join(format(ord(x), "08b")[::-1] for x in data):
                header += (
                    cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
                )
            headers = (header + cls._silence) * 3
        elif mode == "DIGITAL":
            data = "\x00" + ("\xab" * 16) + header_data + ("\xff" * 3)
            for bit in "".join(format(ord(x), "08b")[::-1] for x in data):
                header += (
                    cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
                )
            headers = header + cls._silence
            data = ("\xab" * 16) + header_data + ("\xff" * 3)
            header = AudioSegment.empty()
            for bit in "".join(format(ord(x), "08b")[::-1] for x in data):
                header += (
                    cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
                )
            headers += (header + cls._silence) * 2
        elif mode == "SAGE":
            data = ("\xab" * 16) + header_data + "\xff"
            for bit in "".join(format(ord(x), "08b")[::-1] for x in data):
                header += (
                    cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
                )
            headers = (header + cls._silence) * 3
        elif mode == "TRILITHIC":
            data = ("\xab" * 16) + header_data
            for bit in "".join(format(ord(x), "08b")[::-1] for x in data):
                header += (
                    cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
                )
            headers = (header + cls._silence[:850]) * 3 + cls._silence[:150]
        elif mode == "BROADCASTER":
            data = ("\xab" * 16) + header_data + ("\x00" * 3)
            for bit in "".join(format(ord(x), "08b")[::-1] for x in data):
                header += cls._space(44100) if bit == "0" else cls._mark(44100)
            headers = (header + cls._silence) * 3
        else:
            data = ("\xab" * 16) + header_data
            for bit in "".join(format(ord(x), "08b")[::-1] for x in data):
                header += (
                    cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
                )
            headers = (header + cls._silence) * 3
        return headers

    @classmethod
    def genEOM(cls, mode: str = "", sampleRate: int = 24000):
        """
        Generate SAME _eoms.(Inline Class, can be called without class Init)
        :int sample_rate:
            Audio sample_rate
        Returns a PyDub AudioSegment of the Generated SAME _eoms.
        """
        eom = cls._eom(mode=mode, sample_rate=sampleRate)
        return eom

    @classmethod
    def genEAS(
        cls,
        header: str,
        attentionTone: bool = True,
        endOfMessage: bool = True,
        audio: AudioSegment = AudioSegment.empty(),
        mode: str = "",
        sampleRate: int = 24000,
    ) -> AudioSegment:
        """
        Generate EAS SAME from a String. (Inline Class, can be called without class Init)
        :str hdr:
            Data to be modulated into SAME EAS Data.
        :bool attentionTone:
            Enable Internal Attention Tone (EBS Style 853+960).
        :bool endOfMessage:
            Enable SAME End Of Message bursts.
        :AudioSegment audio:
            Included audio in-between the SAME header Bursts + Attention Tone, and the End Of Message Bursts.
        :str mode:
            Select between "None, SAGE, DIGITAL, TRILITHIC, BROADCASTER, NWS" for "Authentic" Encoder header tones.
        :int sampleRate:
            Audio sample rate
        Returns a PyDub AudioSegment of the Generated Alert.
        """
        sample_rate = sampleRate
        attn_tone = AudioSegment.empty()
        _eoms = AudioSegment.empty()
        headers = cls._header(header=header, mode=mode, sample_rate=sample_rate)
        if audio != AudioSegment.empty():
            audio = (
                audio.set_frame_rate(sample_rate).set_channels(1).set_sample_width(2)
            )
        if attentionTone:
            attn_tone = cls._attn(mode=mode, sample_rate=sample_rate) + cls._silence

        if endOfMessage:
            _eoms = cls.genEOM(mode=mode, sample_rate=sample_rate)
        alert: AudioSegment = (
            cls._silence[:500]
            + headers
            + attn_tone
            + audio
            + _eoms
            + cls._silence[:500]
        )
        if mode == "BROADCASTER":
            alert.set_frame_rate(8000)
        return alert
