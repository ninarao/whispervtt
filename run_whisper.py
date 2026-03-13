#!/usr/bin/env python3

import os
import sys
import platform
from pathlib import Path
import datetime
import shutil
import whisper_with_metadata_vtt as whisper

# sys.argv = [
#     'run_whisper.py',
#     '/Users/nraogra/Desktop/Captioning/whisperdemo/vkttt_7min/data',
#     ]

'''
script to find new video and audio files and run whispervtt on them
'''

def get_media_list(reviewed_dir, time_minus_24, timenow):
    media_list = []
    vid_formats = ['.mp4']
    aud_formats = ['.wav', '.mp3']
    for media in Path(reviewed_dir).rglob('*'):
        if media.suffix in aud_formats or media.suffix in vid_formats:
            c_datestamp = get_time(media)
            if time_minus_24 <= c_datestamp <= timenow:
                mediaName = os.path.basename(media)
                print(f'this was made in the past day: {mediaName} {c_datestamp}')
                media_list.append(media)
        else:
            continue
    if media_list:
        str_media_list = [os.fspath(p) for p in media_list]
    else:
        str_media_list = []
    return str_media_list

def get_time(media):
    if platform.system() == 'Windows':
        c_timestamp = os.path.getctime(media)
        c_datestamp = datetime.datetime.fromtimestamp(c_timestamp)
        return c_datestamp
    else:
        stat = os.stat(media)
        try:
            c_timestamp = stat.st_birthtime
            c_datestamp = datetime.datetime.fromtimestamp(c_timestamp)
        except AttributeError:
            c_timestamp = stat.st_mtime
            c_datestamp = datetime.datetime.fromtimestamp(c_timestamp)
        finally:
            return c_datestamp

def main(reviewed_dir):
    reviewed_dir = sys.argv[1]
    timenow = datetime.datetime.now()
    print(f'time now: {timenow}')
    time_minus_24 = timenow - datetime.timedelta(hours=24)
    print(f'time minus 24: {time_minus_24}')
    vtt_txt_dest = f'{reviewed_dir}/media_run'
    processed_files = f'{reviewed_dir}/processed_files'
    os.chdir(reviewed_dir)
    if not os.path.exists(vtt_txt_dest):
        os.makedirs(vtt_txt_dest)
    if not os.path.exists(processed_files):
        os.makedirs(processed_files)
    media_list = get_media_list(reviewed_dir, time_minus_24, timenow)
    print(f'media list: \n{media_list}')
    if media_list:
        for file in media_list:
            try:
                whisper.whisper_transcribe(file, 'large-v3', None, vtt_txt_dest, None)
            except Exception as e:
                print(f'error "{e}" with running whisper on file {file}')
                continue
            else:
                source_path = os.path.join(reviewed_dir, file)
                dest_path = os.path.join(processed_files, file)
                try:
                    shutil.move(source_path, dest_path)
                except shutil.Error as e:
                    print(f'could not move {file} due to error: "{e}"')

if __name__ == '__main__':
    main(sys.argv[1:])
