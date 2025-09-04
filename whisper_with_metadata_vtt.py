#!/usr/bin/env python3

import glob
import os
import sys
from pathlib import Path
from langcodes import Language
import langcodes
import whisper
from whisper.utils import get_writer
from datetime import date
import pandas as pd

sys.argv = ['whisper_with_metadata_vtt.py', '/Users/nraogra/Desktop/Captioning/metadata_test', '/Users/nraogra/Desktop/Captioning/metadata_test/webvtt_titles.csv']

# check that command has metadata file location and caption folder location
if len(sys.argv) != 3:
    print("Usage: python whisper_with_metadata_vtt.py [media directory] [metadata csv]")
    sys.exit(1)

if not os.path.isdir(sys.argv[1]):
    print("Error: %s is not a valid directory." % sys.argv[1])
    print("Usage: python whisper_with_metadata_vtt.py [media directory] [metadata csv]")
    sys.exit(1)
        
if not os.path.isfile(sys.argv[2]):
    print("Error: %s is not a valid file." % sys.argv[2])
    print("Usage: python whisper_with_metadata_vtt.py [media directory] [metadata csv]")
    sys.exit(1)
        
arg1 = sys.argv[1]
arg2 = sys.argv[2]

print('media directory: ',arg1)
print('metadata csv: ',arg2)

# prompt to choose whisper model
modelchoice = input("what model do you want to use?\noptions: tiny, base, small, medium, large-v3, turbo\n")
while modelchoice not in {"tiny", "base", "small", "medium", "large-v3", "turbo"}:
    print("invalid input.")
    modelchoice = input("what model do you want to use? options: tiny, base, small, medium, large-v3, turbo\n")
print(f"model selected: {modelchoice}")

# prompt to specify language
langg = input("enter the content language or leave blank for auto-detect: ")
if langg != "":
    lang_find = langcodes.find(langg)
    lang_obj3 = Language.get(lang_find).to_alpha3()
    print(f"language: {lang_obj3}")

# check for output folder and create if needed
outputDir = os.path.join(arg1, "output")
print("checking for output folder...")
if not os.path.exists(outputDir):
    os.mkdir(outputDir)
    print("output folder %s created" % outputDir)
else:
    print("output folder %s already exists" % outputDir)


def get_title():
# read metadata from csv
    df = pd.read_csv(arg2, dtype="str", index_col="File")
    try:
        Title = df.at[sourceFile, "Title"]
        if pd.isna(df.at[sourceFile, "Title"]):
            TitleLine = "Title: unknown"
        else:
            TitleLine = f"Title: {Title}"
        return TitleLine
    except KeyError:
        TitleLine = "Title: unknown"
        return TitleLine
    
def get_mediaID():
# read metadata from csv
    df = pd.read_csv(arg2, dtype="str", index_col="File")
    try:
        MediaID = df.at[sourceFile, "Media Identifier"]
        if pd.isna(df.at[sourceFile, "Media Identifier"]):
            MediaIDLine = "Media Identifier: unknown"
        else:
            MediaIDLine = f"Media Identifier: {MediaID}, Emory PID"
        return MediaIDLine
    except KeyError:
        MediaIDLine = "Media Identifier: unknown"
        return MediaIDLine

def get_language():
    model = whisper.load_model(modelchoice)
    audio = whisper.load_audio(mediafile)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)
    _, probs = model.detect_language(mel)
    alpha2 = max(probs, key=probs.get)
#     print(f"Language: {max(probs, key=probs.get)}")
    lang_obj = Language.get(alpha2)
    alpha3 = lang_obj.to_alpha3()
    return alpha3
    

def whisper_transcribe(
    audio_path: str,
    ):

    model = whisper.load_model(modelchoice)
    output_dir = outputDir
    language = "en" if modelchoice.endswith(".en") else langg if langg != "" else None
    result = model.transcribe(
        audio_path, language=language, temperature=0, no_speech_threshold=0.4, word_timestamps=True, task="transcribe"
    )
    word_options = {
        "max_line_count": 2,
        "max_line_width": 32
    }

    vtt_write = get_writer('vtt', output_dir=output_dir)
    vtt_write(result, audio_path, word_options)
    
    outputVTT = f"{outputDir}/{justName}.vtt"
    
    today = str(date.today())
    
    ver = (whisper.__version__)
    
    MediaIDLine = get_mediaID()
    TitleLine = get_title()

    with open (outputVTT, 'rt', encoding="utf8") as newVTT:
        data = newVTT.read()
        mList = [
            "WEBVTT",
            "",
            "Type: caption",
            f"Language: {lango}",
            "Responsible Party: US, Emory University",
            f"{MediaIDLine}",
            f"Originating File: {sourceFile}",
            "File Creator: Whisper",
            f"File Creation Date: {today}",
            f"{TitleLine}",
            "Origin History: Created by Emory Libraries Media Preservation",
            f"Local Usage Element: Software version: v{ver}; Review history: unreviewed"
            ]
        mString = '\n'.join(mList)
        data = data.replace('WEBVTT', mString)
        newVTT.close()
    with open (outputVTT, 'wt', encoding="utf8") as newVTT:
        newVTT.write(data)
        newVTT.close()

# do the thing
ext = ['.mp4', '.mp3']
for mediafile in glob.glob(f"{arg1}/*{ext}"):
    justName = Path(mediafile).stem
    sourceFile = os.path.basename(mediafile)
    outputName = justName + ".vtt"
    outputFile = os.path.join(outputDir, outputName)
    print(f"processing {sourceFile}")
    
    if langg == "":
        lango = get_language()
    else:
        lango = lang_obj3  
    print(f"language: {lango}")
    
    if not os.path.exists(outputFile):
        whisper_transcribe(mediafile)
    else:
        while True:
            print("output file %s already exists, do you want to overwrite? (y/n)" % outputName)
            userDecide = input()
            if userDecide == "n":
                print("skipping file")
                break
            elif userDecide == "y":
                print("overwriting file %s" % outputName)
                whisper_transcribe(mediafile)
                break
