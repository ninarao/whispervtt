# whispervtt
Runs Whisper over a directory of media files.  For each mp4 and mp3 file, it generates a text transcript and a WebVTT caption file with FADGI metadata, using an optional CSV for Title and Media Identifier.

Script is customized for Emory Libraries; FADGI metadata is generated from the script or matched from the CSV as follows:

Element | Source
--- | ---
Type | hard-coded
Language | auto-detected by Whisper or supplied by user
Responsible Party | hard-coded
Media Identifier | matched from CSV
Originating File | generated from media file
File Creator | hard-coded
File Creation Date | generated from script
Title | matched from CSV
Origin History | hard-coded
Local Usage Element: Software version | generated from script
Local Usage Element: Review history | hard-coded

## Requirements:
- [Whisper](https://github.com/openai/whisper)
- [ffmpeg](https://ffmpeg.org/)
- [langcodes](https://pypi.org/project/langcodes/)
