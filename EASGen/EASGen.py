
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
    def __Mark__(cls, sampleRate:int) -> AudioSegment:
        ## Dynamic Samplerate MARK Sine generation
        return Sine(2083.315, sample_rate=sampleRate, bit_depth=8).to_audio_segment(duration=float(1000/520.83), volume=-3)

    @classmethod
    def __Space__(cls, sampleRate:int) -> AudioSegment:
        ## Dynamic Samplerate SAPCE Sine generation
        return Sine(1562.485, sample_rate=sampleRate, bit_depth=8).to_audio_segment(duration=float(1000/520.83), volume=-3)
    
    @classmethod
    def __ATTN__(cls, sampleRate:int):
        return Sine(853, sample_rate=sampleRate, bit_depth=8).to_audio_segment(duration=8000, volume=-10).overlay(Sine(960, sample_rate=sampleRate, bit_depth=8).to_audio_segment(duration=8000, volume=-10))

    @classmethod
    def __EOM__(cls, sampleRate:int):
        EOM = AudioSegment.empty() ## Pregen an AudioSegment object to populate with EOMs on the next line
        for bit in ''.join(format(ord(x), '08b')[::-1] for x in '\xff'+('\xab'*16)+'NNNN\xff'): EOM += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate)
        return (cls.silence + EOM)*3

    @classmethod
    def genEOM(cls, sampleRate:int=24000):
        """
        Generate SAME EOMs.(Inline Class, can be called without class Init)

        :int sampleRate: 
            Audio SampleRate

        Returns a PyDub AudioSegment of the Generated SAME EOMs.
        """
        return cls.__EOM__(sampleRate)

    @classmethod
    def genEAS(cls, header:str, attentionTone:bool=True, endOfMessage:bool=True, audio:AudioSegment=AudioSegment.empty(), sampleRate:int=24000) -> AudioSegment:
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

        :int sampleRate: 
            Audio SampleRate

        Returns a PyDub AudioSegment of the Generated Alert.
        """

        ## Create local variables with Empty AudioSegments for later population if required.
        Header = AudioSegment.empty() 
        ATTNTone = AudioSegment.empty()
        EOMs = AudioSegment.empty()
        
        ##Generate EAS Data
        data = ('\xab'*16)+header ## Adding 16 bytes of Hex AB (Preamble) to the Headers
        for bit in ''.join(format(ord(x), '08b')[::-1] for x in data): ## Recursive loop to go through each byte of our data in LSB
            Header += cls.__Space__(sampleRate) if bit == "0" else cls.__Mark__(sampleRate) ## If bit is a 0, append a Space to the Header Variable, else append a Mark
        Headers = (Header + cls.silence)*3 ##Generate 3 header bursts by multiplying Headers + 1 second of silence by 3

        ## Set Audio to given audio with proper samplerate, channels, and width if provided.
        if audio != AudioSegment.empty():
            audio = audio.set_frame_rate(sampleRate).set_channels(1).set_sample_width(2)	

        ## Add the ATTN tone if requested (Default value is Empty)
        if attentionTone:
            if cls.ATTNTones == AudioSegment.empty():
                ATTNTone = cls.__ATTN__(sampleRate)
            else:
                ATTNTone = (cls.ATTNTones + cls.silence) 	
        
        ## Add the EOMs if requested (Default value is Empty)
        if endOfMessage:
            if cls.EOMs == AudioSegment.empty():
                EOMs = cls.__EOM__(sampleRate)
            else:
                EOMs = cls.EOMs 

        ALERT = cls.silence[:500] + Headers + ATTNTone + audio + EOMs + cls.silence[:500] ## Alert adds 500MS of silence at beginning/end to allow multiple EAS tones played back-to-back to be properly audible.
        return ALERT

    def generateEOMAudio(self):
        """
        Generate SAME EOMs.

        Returns a PyDub AudioSegment of the Generated SAME EOMs.
        """
        return self.EOMs

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
        """

        ## Create local variables with Empty AudioSegments for later population if required.
        Header = AudioSegment.empty() 
        ATTNTone = AudioSegment.empty()
        EOMs = AudioSegment.empty()
        
        ##Generate EAS Data
        data = ('\xab'*16)+header ## Adding 16 bytes of Hex AB (Preamble) to the Headers
        for bit in ''.join(format(ord(x), '08b')[::-1] for x in data): ## Recursive loop to go through each byte of our data in LSB
            Header += self.__Space__(sampleRate) if bit == "0" else self.__Mark__(sampleRate) ## If bit is a 0, append a Space to the Header Variable, else append a Mark
        Headers = (Header + self.silence)*3 ##Generate 3 header bursts by multiplying Headers + 1 second of silence by 3

        ## Set Audio to given audio with proper samplerate, channels, and width if provided.
        if audio != AudioSegment.empty():
            audio = audio.set_frame_rate(sampleRate).set_channels(1).set_sample_width(2)	

        ## Add the ATTN tone if requested (Default value is Empty)
        if attentionTone:
            ATTNTone = (self.ATTNTones + self.silence) 	
        
        ## Add the EOMs if requested (Default value is Empty)
        if endOfMessage:
            EOMs = self.EOMs 

        ALERT = self.silence[:500] + Headers + ATTNTone + audio + EOMs + self.silence[:500] ## Alert adds 500MS of silence at beginning/end to allow multiple EAS tones played back-to-back to be properly audible.
        return ALERT
