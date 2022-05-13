<<<<<<< Updated upstream
# QOscope

# Introduction

# Requirements

# Installation and usage
=======

# qoscope

Qoscope is a fork of [Wicope](https://github.com/diepala/wicope) rewritten for PySide 6.3 using QML.
It's a oscilloscope app with GUI that uses Arduino for signal acquisition. 
The app was created purely for educational purposes and for electronic enthusiasts.

The communication is realized via AVR USART. 
The oscilloscope is capable of acquiring up to 100 kSamples/s.
I currently have a double speed asynchronous mod (U2X) set up in the firmware 
for my own testing and purposes. So there is a smaller error at the expense of the number of samples. 
To turn it off, just delete the U2X setting line in the USART initialization and change 8UL to 16UL 
in the baud prescaler. 

<p align="center">
  <img src="https://github.com/sokolmarek/qoscope/blob/main/assets/screenshot.png?raw=true" />
</p>


## Requirements

`qoscope` requires Python >= 3.8, and PyQt6 or PySide6.
## Installation

Install `qoscope` with pip

```bash
  pip install qoscope
```

or install the latest dev version with:
```bash
  pip install git+https://github.com/sokolmarek/qoscope@main
```

You also need to upload the included firmware to your Arduino board using the 
Arduino IDE (or other software). This is the following file `firmware/firmware.ino`.
    
## Usage/Examples

After uploading the firmware to the Arduino, its pins are used as follows:
* Analog Pin 0 (PC0): Input signal
* Digital Pin 6 (PD6): Trigger signal
* Digital Pin 7 (PD7): Analog trigger threshold level

When using the trigger function it is necessary to have the threshold set on digital 
pin 7 and the signal on digital pin 6 otherwise the arduino will be blocked until it 
receives the trigger. An example circuit with the threshold set to 3V3 might look like this:


<p align="center"> 
  <img src="https://github.com/sokolmarek/qoscope/blob/main/assets/diagram.png?raw=true" /> 
</p>




## Appendix

If anyone wonders about the equation I used for baud prescale (to avoid rounding error)
 or wants useful literature for AVR and USART, for example [AVR articles](http://www.fourwalledcubicle.com/AVRArticles.php) 
 are a pretty good source within a few topics.

>>>>>>> Stashed changes
