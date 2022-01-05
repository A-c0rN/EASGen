![EASGen](https://github.com/A-c0rN/EASGen/blob/main/doc/img/EASGen.png)

![PyPI](https://img.shields.io/pypi/v/EASGen?label=Version&style=flat-square) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/A-c0rN/EASGen/CodeQL?style=flat-square) ![PyPI - Downloads](https://img.shields.io/pypi/dm/EASGen?style=flat-square) ![GitHub language count](https://img.shields.io/github/languages/count/A-c0rN/EASGen?style=flat-square) ![GitHub](https://img.shields.io/github/license/A-c0rN/EASGen?style=flat-square)

A Fast Python EAS Generation Library

## Features
> - [x] EAS Generation 
> - [x] Individual Header, Attention Tone, and EOM Generation
> - [x] Class and Inline Generation Scripts
> - [x] Fast
> - [x] PyDub AudioSegment Output for Easy Integration
> - [x] Audio File Imput for Audio Injection

## Installation
This package should be installable through Pip.

On a Debian Based Linux OS:
```
sudo apt update
sudo apt install python3 python3-pip
pip3 install EASGen
```


On Windows:

[Install Python](https://www.python.org/downloads/)

In CMD:
```
python -m pip install EASGen
```

## Usage
To generate a simple SAME Required Weekly Test:
```python
from EASGen import EASGen
from pydub.playback import play

AlertManager = EASGen.EASGen()
header = "ZCZC-EAS-RWT-005007+0015-0010000-WACNTECH-" ## EAS Header to send
Alert = AlertManager.generateEASAudio(header=header, attentionTone=False, endOfMessage=True) ## Generate an EAS SAME message with no ATTN signal, and with EOMs.
play(Alert) ## Play the EAS Message
```

To use Inline Generation (Slower):
```python
from EASGen import EASGen
from pydub.playback import play

header = "ZCZC-EAS-RWT-005007+0015-0010000-WACNTECH-" ## EAS Header to send
Alert = EASGen.genEAS(header=header, attentionTone=False, endOfMessage=True) ## Generate an EAS SAME message with no ATTN signal, and with EOMs.
play(Alert) ## Play the EAS Message
```