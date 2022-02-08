
from pydub import AudioSegment
from pydub.generators import Sine

class EASGen():
    """Generate various EAS Alert Types.
    """
    
    silence = AudioSegment.silent() ## 1 second silence, Used globally.
    ATTNTones = AudioSegment.empty() ## Empty ATTN AudSegs for later population by the Init.
    EOMs = AudioSegment.empty() ## Empty EOM AudSegs for later population by the Init.


    def __init__(self, sampleRate:int=24000) -> None:

        ## Normal ATTN - This consists of a 853 Hz tone x 960 Hz tone generated at BD 8 and sample of whatever for 8 sec. 
        self.ATTNTones = self.__ATTN__(sampleRate)

        ## Pregen EOMs
        self.EOMs = self.__EOM__(sampleRate) ## Set the Global EOMs to the EOMs we just made, as 1 sec silence + EOM times 3

    @classmethod
    def __Mark__(cls, sampleRate:int=24000) -> AudioSegment:
        ## Dynamic Samplerate MARK Sine generation (One Bit)
        return Sine(2083.315, sample_rate=sampleRate, bit_depth=8).to_audio_segment(duration=float(1000/520.83), volume=-3)

    @classmethod
    def __Space__(cls, sampleRate:int=24000) -> AudioSegment:
        ## Dynamic Samplerate SPACE Sine generation (One Bit)
        return Sine(1562.485, sample_rate=sampleRate, bit_depth=8).to_audio_segment(duration=float(1000/520.83), volume=-3)
    
    @classmethod
    def __ATTN__(cls, mode:str="", sampleRate:int=24000):
        ## Dynamic Samplerate Attention Tone Generation
        if mode == "NWS":
            return Sine(1050, sample_rate=sampleRate, bit_depth=8).to_audio_segment(duration=9000, volume=-4)
        else:
            return Sine(853, sample_rate=sampleRate, bit_depth=8).to_audio_segment(duration=8000, volume=-10).overlay(Sine(960, sample_rate=sampleRate, bit_depth=8).to_audio_segment(duration=8000, volume=-10))

    @classmethod
    def __EOM__(cls, mode:str="", sampleRate:int=24000):
        EOM = AudioSegment.empty() ## Pregen an AudioSegment object to populate with EOMs on the next lines
        if mode == "NWS":
            for bit in ''.join(format(ord(x), '08b')[::-1] for x in ('\xab'*16)+'NNNN'+('\x00'*2)): EOM += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate)
            return (cls.silence + EOM)*3
        elif mode == "DIGITAL":
            for bit in ''.join(format(ord(x), '08b')[::-1] for x in '\x00'+('\xab'*16)+'NNNN'+('\xff'*3)): EOM += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate)
            data = cls.silence + EOM
            EOM = AudioSegment.empty() ## Clear EOM value to make Juju stoof not happen.
            for bit in ''.join(format(ord(x), '08b')[::-1] for x in ('\xab'*16)+'NNNN'+('\xff'*3)): EOM += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate)
            data += (cls.silence + EOM)*2
            return data
        elif mode == "SAGE":
            for bit in ''.join(format(ord(x), '08b')[::-1] for x in ('\xab'*16)+'NNNN\xff'): EOM += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate)
            return (cls.silence + EOM)*3
        elif mode == "TRILITHIC":
            for bit in ''.join(format(ord(x), '08b')[::-1] for x in ('\xab'*16)+'NNNN'): EOM += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate)
            return (cls.silence[:850] + EOM)*3
        else:
            for bit in ''.join(format(ord(x), '08b')[::-1] for x in ('\xab'*16)+'NNNN'): EOM += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate)
            return (cls.silence + EOM)*3


    @classmethod
    def genEOM(cls, mode:str="", sampleRate:int=24000):
        """
        Generate SAME EOMs.(Inline Class, can be called without class Init)

        :int sampleRate: 
            Audio SampleRate

        Returns a PyDub AudioSegment of the Generated SAME EOMs.
        """
        if cls.EOMs != AudioSegment.empty():
            EOM = cls.EOMs
        else:
            EOM = cls.__EOM__(mode=mode, sampleRate=sampleRate)
        return EOM

    @classmethod
    def genEAS(cls, header:str, attentionTone:bool=True, endOfMessage:bool=True, audio:AudioSegment=AudioSegment.empty(), mode:str="", sampleRate:int=24000) -> AudioSegment:
        """
        Generate EAS SAME from a String. (Inline Class, can be called without class Init)

        :str hdr: 
            Data to be modulated into SAME EAS Data.

        :bool attentionTone: 
            Enable Internal Attention Tone (EBS Style 853+960).

        :bool endOfMessage: 
            Enable SAME End Of Message bursts.

        :AudioSegment audio: 
            Included audio in-between the SAME Header Bursts + Attention Tone, and the End Of Message Bursts.

        :str mode: 
            Select between "None, SAGE, DIGITAL, TRILITHIC, NWS" for "Authentic" Encoder header tones.

        :int sampleRate: 
            Audio SampleRate

        Returns a PyDub AudioSegment of the Generated Alert.
        """

        ## Create local variables with Empty AudioSegments for later population if required.
        Header = AudioSegment.empty() 
        ATTNTone = AudioSegment.empty()
        EOMs = AudioSegment.empty()
        
        ##Generate EAS Data
        if mode == "NWS":
            data = ('\xab'*16)+header+('\x00'*2) ## Adding 16 bytes of Hex AB (Preamble) to the Headers (And 2 byes of Hex 00 to end of headers for "NWS" style)
            for bit in ''.join(format(ord(x), '08b')[::-1] for x in data): ## Recursive loop to go through each byte of our data in LSB
                Header += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate) ## If bit is a 0, append a Space to the Header Variable, else append a Mark
            Headers = (Header + cls.silence)*3 ##Generate 3 header bursts by multiplying Headers + 1 second of silence by 3
        elif mode == "DIGITAL":
            data = '\x00'+('\xab'*16)+header+('\xff'*3) ## Adding 16 bytes of Hex AB (Preamble) to the Headers (And 3 byes of Hex FF to end of headers for "SAGE DIGITAL style" headers)
            for bit in ''.join(format(ord(x), '08b')[::-1] for x in data): ## Recursive loop to go through each byte of our data in LSB
                Header += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate) ## If bit is a 0, append a Space to the Header Variable, else append a Mark
            Headers = Header + cls.silence ##Generate a header burst of the first header with the chirp. (SAGE Digital is Annoying AF)
            data = ('\xab'*16)+header+('\xff'*3) ## Adding 16 bytes of Hex AB (Preamble) to the Headers (And 3 byes of Hex FF to end of headers for "SAGE DIGITAL style" headers)
            Header = AudioSegment.empty() ## Clear header value to make Juju stoof not happen.
            for bit in ''.join(format(ord(x), '08b')[::-1] for x in data): ## Recursive loop to go through each byte of our data in LSB
                Header += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate) ## If bit is a 0, append a Space to the Header Variable, else append a Mark
            Headers += (Header + cls.silence)*2 ##Generate 2 header bursts of the last 2 headers without the chirp. (SAGE Digital is REALLY Annoying AF)
        elif mode == "SAGE":
            data = ('\xab'*16)+header+'\xff' ## Adding 16 bytes of Hex AB (Preamble) to the Headers (And 1 byte of Hex FF to end of headers for "SAGE EAS style" headers)
            for bit in ''.join(format(ord(x), '08b')[::-1] for x in data): ## Recursive loop to go through each byte of our data in LSB
                Header += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate) ## If bit is a 0, append a Space to the Header Variable, else append a Mark
            Headers = (Header + cls.silence)*3 ##Generate 3 header bursts by multiplying Headers + 1 second of silence by 3
        elif mode == "TRILITHIC":
            data = ('\xab'*16)+header ## Adding 16 bytes of Hex AB (Preamble) to the Headers (And 2 byes of Hex 00 to end of headers for "NWS" style)
            for bit in ''.join(format(ord(x), '08b')[::-1] for x in data): ## Recursive loop to go through each byte of our data in LSB
                Header += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate) ## If bit is a 0, append a Space to the Header Variable, else append a Mark
            Headers = (Header + cls.silence[:850])*3+cls.silence[:150] ##Generate 3 header bursts by multiplying Headers + 0.85 second of silence by 3 (Smaller silence for "Trilithic style")
        else:
            data = ('\xab'*16)+header## Adding 16 bytes of Hex AB (Preamble) to the Headers
            for bit in ''.join(format(ord(x), '08b')[::-1] for x in data): ## Recursive loop to go through each byte of our data in LSB
                Header += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate) ## If bit is a 0, append a Space to the Header Variable, else append a Mark
            Headers = (Header + cls.silence)*3 ##Generate 3 header bursts by multiplying Headers + 1 second of silence by 3

        ## Set Audio to given audio with proper samplerate, channels, and width if provided.
        if audio != AudioSegment.empty():
            audio = audio.set_frame_rate(sampleRate).set_channels(1).set_sample_width(2)	

        ## Add the ATTN tone if requested (Default value is Empty)
        if attentionTone:
            if cls.ATTNTones == AudioSegment.empty():
                ATTNTone = (cls.__ATTN__(mode=mode, sampleRate=sampleRate) + cls.silence)
            else:
                ATTNTone = (cls.ATTNTones + cls.silence) 	
        
        ## Add the EOMs if requested (Default value is Empty)
        if endOfMessage:
            EOMs = cls.genEOM(mode=mode, sampleRate=sampleRate)

        ALERT = cls.silence[:500] + Headers + ATTNTone + audio + EOMs + cls.silence[:500] ## Alert adds 500MS of silence at beginning/end to allow multiple EAS tones played back-to-back to be properly audible.
        return ALERT

    def generateEOMAudio(self, sampleRate:int=24000):
        """
        Generate SAME EOMs.

        Returns a PyDub AudioSegment of the Generated SAME EOMs.
        Please note, Custom Style Headers are not supported with this class.
        """
        return self.genEOM(sampleRate=sampleRate)

    def generateEASAudio(self, header:str, attentionTone:bool=True, endOfMessage:bool=True, audio:AudioSegment=AudioSegment.empty(), sampleRate:int=24000) -> AudioSegment:
        """
        Generate EAS SAME from a String.

        :str hdr: 
            Data to be modulated into SAME EAS Data.

        :bool attentionTone: 
            Enable Internal Attention Tone (EBS Style 853+960).

        :bool endOfMessage: 
            Enable SAME End Of Message bursts.

        :AudioSegment audio: 
            Included audio in-between the SAME Header Bursts + Attention Tone, and the End Of Message Bursts.

        :int sampleRate: 
            Audio SampleRate

        Returns a PyDub AudioSegment of the Generated Alert.
        Please note, Custom Style Headers are not supported with this class.
        """
        ALERT = self.genEAS(header=header, attentionTone=attentionTone, endOfMessage=endOfMessage, audio=audio, sampleRate=sampleRate)
        return ALERT
