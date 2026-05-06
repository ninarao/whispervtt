#!/usr/bin/env python3

import os
import sys
import platform
from pathlib import Path
import datetime
import shutil
import whispervtt as whisper

sys.argv = [
    'run_whisper.py',
    '/Users/nraogra/Desktop/Captioning/whisperdemo/vkttt_7min/data',
    ]

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

def run_whisper(media_list, vtt_txt_dest, processed_media, reviewed_dir, log_source, timenow):
    os.chdir(reviewed_dir)
    txt_header = True
    for file in media_list:
        mediaName = os.path.basename(file)
        try:
            whisper.whisper_transcribe(file, 'large-v3', None, vtt_txt_dest, None, txt_header)
            print(f'ran whisper on file {mediaName}')
            generate_log(log_source, timenow, f'ran whisper on file {mediaName}')
            source_path = os.path.join(reviewed_dir, file)
            dest_path = os.path.join(processed_media, mediaName)
            try:
                shutil.move(source_path, dest_path)
                generate_log(log_source, timenow, f'moved {mediaName} to {processed_media}')
            except shutil.Error as e:
                print(f'could not move {mediaName} due to error: "{e}"')
                generate_log(log_source, timenow, f'could not move {mediaName} due to error: "{e}"')
                continue
        except Exception as e:
            print(f'could not run whisper on file {mediaName} due to error: "{e}"')
            generate_log(log_source, timenow, f'could not run whisper on file {mediaName} due to error: "{e}"')
            continue

def generate_log(log, timenow, what2log):
    if not os.path.isfile(log):
        with open(log, "w", encoding='utf-8') as f:
            f.write(timenow.strftime("%Y-%m-%d %H:%M:%S%p")
                     + '\n' + what2log + '\n')
    else:
        with open(log, "a", encoding='utf-8') as f:
            f.write(timenow.strftime("%Y-%m-%d %H:%M:%S%p")
                     + '\n' + what2log + '\n')

def main(reviewed_dir):
    reviewed_dir = Path(sys.argv[1])
    timenow = datetime.datetime.now()
    print(f'time now: {timenow}')
    time_minus_24 = timenow - datetime.timedelta(hours=24)
    print(f'time minus 24: {time_minus_24}')
    vtfolder = 'vtt_txt_files'
    vtt_txt_dest = os.path.join(reviewed_dir, vtfolder)
    procfolder = 'processed_media'
    processed_media = os.path.join(reviewed_dir, procfolder)
    logname = 'run_whisp_log.txt'
    log_source = os.path.join(reviewed_dir, logname)
    os.chdir(reviewed_dir)
    if not os.path.exists(vtt_txt_dest):
        os.makedirs(vtt_txt_dest)
    if not os.path.exists(processed_media):
        os.makedirs(processed_media)
    media_list = get_media_list(reviewed_dir, time_minus_24, timenow)
    if media_list:
        print(f'media list: \n{media_list}')
        generate_log(log_source, timenow, f'media list: \n{media_list}')
        run_whisper(media_list, vtt_txt_dest, processed_media, reviewed_dir, log_source, timenow)
    else:
        print('no files in media list')
        generate_log(log_source, timenow, 'no files in media list')

if __name__ == '__main__':
    main(sys.argv[1:])
