#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import datetime
import shutil

# sys.argv = [
#     'move_vtts.py',
#     '/Users/nraogra/Desktop/Captioning/whisperdemo/vkttt_7min/data/vtt_txt_files',
#     '/Users/nraogra/Desktop/Captioning/whisperdemo/vkttt_7min/data/output/sync_for_review',
#     '/Users/nraogra/Desktop/Captioning/whisperdemo/vkttt_7min/data/output/move_here'
#     ]

'''
script to find vtt and txt files,
copy them to sync folder for review,
and move them to staging folder
'''

def get_file_list(file_dir):
    file_list = []
    file_formats = ['.vtt', '.txt']
    for file in Path(file_dir).rglob('*'):
        if os.path.isfile(file):
            if file.suffix in file_formats:
                file_list.append(file)
            else:
                continue
        else:
            continue
        if file_list:
            str_file_list = [os.fspath(p) for p in file_list]
        else:
            str_file_list = ""
    return str_file_list

def copy_files(file_list, file_dir, sync_dir, review_dir, log_source, timenow):
    os.chdir(file_dir)
    for file in file_list:
        fileName = os.path.basename(file)
        justName = Path(file).stem
        fileExt = Path(file).suffix
        datesuffix = str(timenow.strftime("%Y%m%d-%H%M"))
        source_path = os.path.join(file_dir, fileName)
        dest_path = os.path.join(sync_dir, fileName)
        if os.path.exists(dest_path):
            newName = justName + "_" + datesuffix + fileExt
            print(f'file {justName}{fileExt} already exists in {sync_dir}, copying as {newName}')
            try:
                dest_path = os.path.join(sync_dir, newName)
                shutil.copy2(source_path, dest_path)
                generate_log(log_source, timenow, f'copied {fileName} as {newName} to {sync_dir}')
                copied = True
            except shutil.Error as e:
                print(f'could not copy {fileName} due to error: "{e}"')
                generate_log(log_source, timenow, f'could not copy {fileName} due to error: "{e}"')
                continue
        else:
            try:
                shutil.copy2(source_path, dest_path)
                generate_log(log_source, timenow, f'copied {fileName} to {sync_dir}')
                copied = True
            except shutil.Error as e:
                print(f'could not copy {fileName} due to error: "{e}"')
                generate_log(log_source, timenow, f'could not copy {fileName} due to error: "{e}"')
                continue
        if copied:
            move_file(fileName, justName, file_dir, fileExt, review_dir, log_source, datesuffix, timenow)

def move_file(fileName, justName, file_dir, fileExt, review_dir, log_source, datesuffix, timenow):
    os.chdir(file_dir)
    source_path = os.path.join(file_dir, fileName)
    dest_path = os.path.join(review_dir, fileName)
    print(source_path)
    print(dest_path)
    if os.path.exists(dest_path):
        newName = justName + "_" + datesuffix + fileExt
        print(f'file {justName}{fileExt} already exists in {review_dir}, moving as {newName}')
        try:
            dest_path = os.path.join(review_dir, newName)
            shutil.move(source_path, dest_path)
            generate_log(log_source, timenow, f'moved {fileName} as {newName} to {review_dir}')
        except shutil.Error as e:
            print(f'could not move {fileName} due to error: "{e}"')
            generate_log(log_source, timenow, f'could not move {fileName} due to error: "{e}"')
    else:
        try:
            shutil.move(source_path, dest_path)
            generate_log(log_source, timenow, f'moved {fileName} to {review_dir}')
        except shutil.Error as e:
            print(f'could not move {fileName} due to error: "{e}"')
            generate_log(log_source, timenow, f'could not move {fileName} due to error: "{e}"')

def generate_log(log, timenow, what2log):
    if not os.path.isfile(log):
        with open(log, "w", encoding='utf-8') as f:
            f.write(timenow.strftime("%Y-%m-%d %H:%M:%S%p")
                     + '\n' + what2log + '\n')
    else:
        with open(log, "a", encoding='utf-8') as f:
            f.write(timenow.strftime("%Y-%m-%d %H:%M:%S%p")
                     + '\n' + what2log + '\n')

def main(file_dir):
    file_dir = sys.argv[1]
    sync_dir = sys.argv[2]
    review_dir = sys.argv[3]
    log_source = f'{file_dir}/move_vtt_txt_log.log'
    timenow = datetime.datetime.now()
    os.chdir(file_dir)
    file_list = get_file_list(file_dir)
    if file_list:
        print('vtt and txt list:')
        print(*file_list, sep='\n')
        generate_log(log_source, timenow, f'vtt and txt list: \n{file_list}')
        copy_files(file_list, file_dir, sync_dir, review_dir, log_source, timenow)
    else:
        print('no vtt or txt files in file list')
        generate_log(log_source, timenow, 'no vtt or txt files in file list')

if __name__ == '__main__':
    main(sys.argv[1:])