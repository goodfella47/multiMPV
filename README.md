# multiMPV 
multiMPV is a wrapper for the mpv media player that allows you to play multiple video files simultaneously in a single window and in a convenient way. It supports up to 9 video streams.

## Installation
multiMPV can run as a python script or as an executable file.
Download and extract mpv media player from https://mpv.io/. to run as an executable, either download and extract a release zip or download this repository and build it using the build instructions bellow and open multiMPV.exe. 
alternatively, run the multiMPV.py script using python 3.8 or greater. 
the first run will prompt you to select an mpv executable file.

## Usage
multiMPV accepts mp4,mkv and avi video formats. it also accepts txt files with video filenames, it will search for these files in the default_vid_destination folder that can be changed in the config.ini file.

## Build instructions
  1. Install pyinstaller from https://www.pyinstaller.org/. 
  2. Download or clone this repository.
  3. Build multiMPV using the command ```pyinstaller multiMPV.py```
  4. copy config.ini and portable_config folder to the multiMPV executable folder.
