#!/usr/bin/env python3

import glob
import os
import argparse
import sys
from pathlib import Path
from langcodes import Language
import langcodes
import whisper
from whisper.utils import get_writer
from datetime import date
import pandas as pd

# sys.argv = [
#     'whispervtt.py',
#     '/Users/nraogra/Desktop/Captioning/whisperdemo/vkttt_7min/data',
#     '-o'
#     ]

def valid_directory(path_string):
    if not os.path.isdir(path_string):
        raise argparse.ArgumentTypeError(f"'{path_string}' is not a valid directory.")
    return path_string

def valid_csv(path_csv):
    if not os.path.isfile(path_csv):
        raise argparse.ArgumentTypeError(f"'{path_csv}' is not a valid csv file.")
    if not path_csv.endswith(".csv"):
        raise argparse.ArgumentTypeError(f"'{path_csv}' is not a valid csv file.")
    else:
        return path_csv

# sets media directory, optional csv, and overwrite option
def setup(args_):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "media_directory",
        type=valid_directory,
        help="Directory of media files"
        )
    parser.add_argument(
        "-c", "--csv",
        type=valid_csv,
        help="Metadata CSV"
        )
    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="overwrite any existing output files"
        )

    args = parser.parse_args(args_)
    return args

def choose_model():
    modelchoice = input("what model do you want to use?\noptions: tiny, base, small, medium, large-v3, turbo\n")
    while modelchoice not in {"tiny", "base", "small", "medium", "large-v3", "turbo"}:
        print("invalid input.")
        modelchoice = input("what model do you want to use? options: tiny, base, small, medium, large-v3, turbo\n")
    print(f"model selected: {modelchoice}")
    return modelchoice

def choose_lang():
    while True:
        langg = input("enter the content language or leave blank for auto-detect: ")
        if langg == "":
            langchoice = None
            print("auto-detecting language")
            return langchoice
        elif langg != "":
            try:
                find_lang = langcodes.find(langg)
                langchoice = str(find_lang)
                lang_obj3 = Language.get(find_lang).to_alpha3()
                print(f"language: {lang_obj3}")
                return langchoice
            except LookupError as e:
                print(f'error: {e}')

# check for output folder and create if needed
def output_direct(arg1):
    outputDir = os.path.join(arg1, "output")
    print("checking for output folder...")
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
        print("output folder %s created" % outputDir)
    else:
        print("output folder %s already exists" % outputDir)
    return outputDir

def get_title(mediaf, arg2):
    if arg2 == None:
        TitleLine = "Title: unknown"
        return TitleLine
    else:
    # read metadata from csv
        sourceFile = os.path.basename(mediaf)
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
    
def get_mediaID(mediaf, arg2):
    if arg2 == None:
        MediaIDLine = "Media Identifier: unknown"
        return MediaIDLine
    else:
    # read metadata from csv
        sourceFile = os.path.basename(mediaf)
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

def get_language(mediaf, modelo):
    model = whisper.load_model(modelo)
    audio = whisper.load_audio(mediaf)
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
    modell,
    langchoice,
    outputDir,
    arg2
    ):
    
    if langchoice == None:
        lango = get_language(audio_path, modell)
    else:
        lango = langchoice  
        print(f"language: {lango}")

    model = whisper.load_model(modell)
    output_dir = outputDir
    options = whisper.DecodingOptions().__dict__.copy()
    options['beam_size'] = 10
    options['best_of'] = 5
    options['task'] = "transcribe"
    options['language'] = "en" if modell.endswith(".en") else langchoice if langchoice != None else None
    result = model.transcribe(
        audio_path, 
        verbose=True,
        no_speech_threshold=0.4,
        condition_on_previous_text=False, 
        word_timestamps=True, 
        **options
        )
    
    txt_write = get_writer('txt', output_dir=output_dir)
    txt_write(result, audio_path)
    
    word_options = {
        "max_line_count": 2,
        "max_line_width": 32
    }

    vtt_write = get_writer('vtt', output_dir=output_dir)
    vtt_write(result, audio_path, word_options)
    
    justName = Path(audio_path).stem
    sourceFile = os.path.basename(audio_path)
    
    outputVTT = f"{outputDir}/{justName}.vtt"
    
    today = str(date.today())
    
    ver = (whisper.__version__)
    
    MediaIDLine = get_mediaID(audio_path, arg2)
    TitleLine = get_title(audio_path, arg2)

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
            f"Local Usage Element: [software version] v{ver}; [review history] unreviewed"
            ]
        mString = '\n'.join(mList)
        data = data.replace('WEBVTT', mString)
        newVTT.close()
    with open (outputVTT, 'wt', encoding="utf8") as newVTT:
        newVTT.write(data)
        newVTT.close()

def main(args_):
    args = setup(args_)
    
    arg1 = args.media_directory
    print('media directory: ',arg1)
    
    if args.csv == None:
        arg2 = None
        print("No csv")
    else:
        arg2 = args.csv
        print('metadata csv: ',arg2)

    if args.overwrite == True:
        print("Existing output files will be overwritten.")
    
    outputDir = output_direct(arg1)
    langchoice = choose_lang()
    modelchoice = choose_model()
    
    ext = ['.mp4', '.mp3', '.wav']
    for mediafile in glob.glob(f"{arg1}/*{ext}"):
        if os.path.isfile(mediafile):
            justName = Path(mediafile).stem
            sourceFile = os.path.basename(mediafile)
            outputName = justName + ".vtt"
            outputFile = os.path.join(outputDir, outputName)
            print(f"processing {sourceFile}")
                    
            if not os.path.exists(outputFile):
                whisper_transcribe(mediafile, modelchoice, langchoice, outputDir, arg2)
            elif args.overwrite == True:
                whisper_transcribe(mediafile, modelchoice, langchoice, outputDir, arg2)
            else:
                while True:
                    print("output file %s already exists, do you want to overwrite? (y/n)" % outputName)
                    userDecide = input()
                    if userDecide == "n":
                        print("skipping file")
                        break
                    elif userDecide == "y":
                        print("overwriting file %s" % outputName)
                        whisper_transcribe(mediafile, modelchoice, langchoice, outputDir, arg2)
                        break

if __name__ == '__main__':
    main(sys.argv[1:])
