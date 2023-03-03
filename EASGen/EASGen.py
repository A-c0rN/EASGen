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
    def _nws_attn(cls, sample_rate: int = 24000) -> AudioSegment:
        return Sine(1050, sample_rate=sample_rate, bit_depth=16).to_audio_segment(
            duration=9000, volume=-4
        )

    @classmethod
    def _ebs_attn(cls, sample_rate: int = 24000) -> AudioSegment:
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
    def _npas_attn(cls, sample_rate: int = 24000) -> AudioSegment:
        npas = Sine(3135.96, sample_rate=sample_rate, bit_depth=16).to_audio_segment(
            duration=8000, volume=-10
        )
        high = (
            Sine(1046.5, sample_rate=sample_rate, bit_depth=16)
            .to_audio_segment(duration=500, volume=-10)
            .overlay(
                Sine(932.33, sample_rate=sample_rate, bit_depth=16).to_audio_segment(
                    duration=500, volume=-10
                )
            )
        )
        low = (
            Sine(659.26, sample_rate=sample_rate, bit_depth=16)
            .to_audio_segment(duration=500, volume=-10)
            .overlay(
                Sine(440, sample_rate=sample_rate, bit_depth=16).to_audio_segment(
                    duration=500, volume=-10
                )
            )
        )
        return npas.overlay((high + low) * 8)

    @classmethod
    def genATTN(
        cls, 
        mode: str = "", 
        sampleRate: int = 24000, 
        bandpass: bool = False
    ) -> AudioSegment:
        """Dynamic Attention Tone generation.

        Args:
            mode (str, optional): Attention Tone Generation Emulation. Defaults to None.
            sample_rate (int, optional): WAV sample rate. Defaults to 24000.
            bandpass (bool, optional): Bandpass EAS Audio. Defaults to False.
        """
        sample_rate = sampleRate
        attn = AudioSegment.empty()
        if mode == "NWS":
            attn = cls._nws_attn(sample_rate)
        elif mode == "WEA":
            tone = cls._ebs_attn(sample_rate)
            silence = cls._silence[:500]
            attn = (tone[:2000] + silence + (tone[:1000] + silence) * 2) * 2
        elif mode == "NPAS":
            attn = cls._npas_attn(sample_rate) + cls._silence
        else:
            attn = cls._ebs_attn(sample_rate)
        if bandpass:
            attn = attn.low_pass_filter(800).high_pass_filter(1600)
        return attn

    @classmethod
    def genHeader(
        cls, 
        header_data: str, 
        mode: str = "", 
        sampleRate: int = 24000, 
        bandpass: bool = False
    ) -> AudioSegment:
        """Dynamic EAS header generation.

        Args:
            header (str): EAS Data String. Required.
            mode (str, optional): EAS Generation Encoder Emulation. Defaults to None.
            sample_rate (int, optional): WAV sample rate. Defaults to 24000.
            bandpass (bool, optional): Bandpass EAS Audio. Defaults to False.
        """
        sample_rate = sampleRate
        header = AudioSegment.empty()
        headers = AudioSegment.empty()
        if mode == "NWS":
            data = ("\xab" * 16) + header_data + ("\x00" * 2)
            for bit in "".join(format(ord(x), "08b")[::-1] for x in data):
                header += (
                    cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
                )
            headers = (header + cls._silence) * 3 + cls._silence
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
        elif mode == "NPAS" or mode == "WEA":
            pass
        else:
            data = ("\xab" * 16) + header_data
            for bit in "".join(format(ord(x), "08b")[::-1] for x in data):
                header += (
                    cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
                )
            headers = (header + cls._silence) * 3
        if bandpass:
            headers = headers.low_pass_filter(800).high_pass_filter(1600)
        return headers

    @classmethod
    def genEOM(
        cls, 
        mode: str = "", 
        sampleRate: int = 24000, 
        bandpass: bool = False
    ) -> AudioSegment:
        """Dynamic EOM Generation.

        Args:
            mode (str, optional): EAS Generation Encoder Emulation. Defaults to None.
            sample_rate (int, optional): WAV sample rate. Defaults to 24000.
            bandpass (bool, optional): Bandpass EAS Audio. Defaults to False.
        """
        sample_rate = sampleRate
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
        elif mode == "NPAS" or mode == "WEA":
            pass
        else:
            for bit in "".join(
                format(ord(x), "08b")[::-1] for x in ("\xab" * 16) + "NNNN"
            ):
                eom += cls._space(sample_rate) if bit == "0" else cls._mark(sample_rate)
            eoms = (cls._silence + eom) * 3
        if bandpass:
            eoms = eoms.low_pass_filter(800).high_pass_filter(1600)
        return eoms

    @classmethod
    def genEAS(
        cls,
        header: str = "",
        attentionTone: bool = True,
        endOfMessage: bool = True,
        audio: AudioSegment = AudioSegment.empty(),
        mode: str = "",
        sampleRate: int = 24000, 
        bandpass: bool = False
    ) -> AudioSegment:
        """Mainline EAS Generation

        Args:
            header (str): EAS Data String. Required.
            attentionTone (bool, optional): Attention Tone Generation Flag. Defaults to True.
            endOfMessage (bool, optional): End of Message Generation Flag. Defaults to True.
            audio (AudioSegment, optional): Audio object (Inserted into Message). Defaults to Empty.
            mode (str, optional): EAS Generation Encoder Emulation. Defaults to None.
            sample_rate (int, optional): WAV sample rate. Defaults to 24000.
            bandpass (bool, optional): Bandpass EAS Audio. Defaults to False.
        """
        sample_rate = sampleRate
        attn_tone = AudioSegment.empty()
        eoms = AudioSegment.empty()
        headers = cls.genHeader(header_data=header, mode=mode, sampleRate=sample_rate)

        if audio != AudioSegment.empty():
            audio = (
                audio.set_frame_rate(sample_rate).set_channels(1).set_sample_width(2)
            )
        if attentionTone or mode == "NPAS" or mode == "WEA":
            attn_tone = cls.genATTN(mode=mode, sampleRate=sample_rate) + cls._silence

        if endOfMessage:
            eoms = cls.genEOM(mode=mode, sampleRate=sample_rate)
        alert: AudioSegment = (
            cls._silence[:500] + headers + attn_tone + audio + eoms + cls._silence[:500]
        )
        if bandpass:
            alert = alert.low_pass_filter(800).high_pass_filter(1600)
        return alert

    @classmethod
    def export_wav(
        cls,
        filename: str,
        audio: AudioSegment,
        sample_rate: int = 24000,
        channels: int = 1,
    ):
        """Proper WAV File exporting

        Args:
            filename (str): WAV Filename
            audio (AudioSegment): WAV Audio
            sample_rate (int, optional): WAV sample rate. Defaults to 24000.
            channels (int, optional): WAV Channels. Defaults to 1.
        """
        audio.set_channels(channels=channels).set_frame_rate(
            frame_rate=sample_rate
        ).set_sample_width(sample_width=2)
        audio.export(
            filename,
            format="wav",
            codec="pcm_s16le",
        )
