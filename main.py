#Libraries import (if you do not own the library, in you terminal type in 'pip install library_name'):
from datetime import datetime as dt
import schedule
import hashlib
import shutil
import time
import os
import re

#Constants definition:
BACKUP_SCHEDULE = int(input("How often in minutes would you like to backup your files? Default is 10 minutes (please enter a digit, exemple 10): ") or 10)
SOURCE = input("Enter the source directory path (exemple: c:/Users/ian/source): ")
REPLICA = input("Enter the replica directory path (exemple: c:/Users/ian/replica): ")
LOG = input("Enter the log directory path (exemple: c:/Users/ian/log): ")

#Verify if the directories inputed by the user exist, if not, create them.
if not os.path.exists(SOURCE):
    os.makedirs(SOURCE)
    LOG_INFOS += f"""{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The folder {SOURCE} could not be found and was created.\n"""

if not os.path.exists(REPLICA):
    shutil.copytree(SOURCE, REPLICA) #if the replica directory does not exist, copy directly the content of the source folder in the replica directory.
    LOG_INFOS += f"""{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The folder {REPLICA} could not be found and was created.
{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The content from {SOURCE} was copied in {REPLICA}.\n"""

if not os.path.exists(LOG):
    os.makedirs(LOG)
    LOG_INFOS += f"""{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The folder {LOG} could not be found and was created.\n"""

#This function create a MD5 hash for a file.
def compute_md5(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def backup_script():
    #Define my constant as global to be able to use them in my function
    global SOURCE, REPLICA, LOG
    
    LOG_INFOS = f"Log for the {dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')} \n"

    #Verify if the directories inputed by the user exist, if not, create them.
    if not os.path.exists(SOURCE):
        os.makedirs(SOURCE)
        LOG_INFOS += f"""{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The folder {SOURCE} could not be found and was created.\n"""

    if not os.path.exists(REPLICA):
        shutil.copytree(SOURCE, REPLICA) #if the replica directory does not exist, copy directly the content of the source folder in the replica directory.
        LOG_INFOS += f"""{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The folder {REPLICA} could not be found and was created.
    {dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The content from {SOURCE} was copied in {REPLICA}.\n"""

    if not os.path.exists(LOG):
        os.makedirs(LOG)
        LOG_INFOS += f"""{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The folder {LOG} could not be found and was created.\n"""
        
    #Variables definition:
    log_file_path = f"{LOG}/log_{dt.now().strftime('%d%m%Y_%H%M%S')}.txt" #The name of the log is log_DayMonthYear_HoursMinutesSeconds.txt
    source_folder_name = re.search(r"\/([^\\\/\:\*\?\"\<\>\|]+)$", SOURCE)[1]
    replica_folder_name = re.search(r"\/([^\\\/\:\*\?\"\<\>\|]+)$", REPLICA)[1]
    source_paths_list = [SOURCE]
    source_files_infos = []
    replica_paths_list = [REPLICA]
    replica_files_infos = []

    #This loop create a list of all the subfolder paths in the source directory.
    for root, dirs, files in os.walk(SOURCE):
        for dir in dirs:
            source_paths_list.append(f"{root}/{dir}".replace('\\', '/'))

    #This loop create a list of dictionnaries of all the files in the source directory with their folder location, their name and a unique MD5 hash.
    for folder in source_paths_list:
        for element in os.listdir(folder):
            if os.path.isfile(folder+"/"+element):
                try:
                    source_files_infos.append(dict(
                        folder = re.search(r"{}\/(.+)".format(source_folder_name), folder)[1],
                        filename = f"{element}",
                        hash = compute_md5(folder+'/'+element)))
                except:
                    source_files_infos.append(dict(
                        folder = source_folder_name,
                        filename = f"{element}",
                        hash = compute_md5(folder+'/'+element)))

    #This loop create a list of all the subfolder paths in the replica directory.
    for root, dirs, files in os.walk(REPLICA):
        for dir in dirs:
            #append the file name to the list
            replica_paths_list.append(f"{root}/{dir}".replace('\\', '/'))

    #This loop create a list of dictionnaries of all the files in the source directory with their folder location, their name and a unique MD5 hash.
    for folder in replica_paths_list:
        for element in os.listdir(folder):
            if os.path.isfile(folder+"/"+element):
                try:
                    replica_files_infos.append(dict(
                        folder = re.search(r"{}\/(.+)".format(replica_folder_name), folder)[1],
                        filename = f"{element}",
                        hash = compute_md5(folder+'/'+element)))
                except:
                    replica_files_infos.append(dict(
                        folder = source_folder_name,
                        filename = f"{element}",
                        hash = compute_md5(folder+'/'+element)))

    #If the replica directory is empty, copy the content from the source directory directly. 
    if not replica_files_infos:
        shutil.copytree(SOURCE, REPLICA, dirs_exist_ok="dirs_exist_ok")
        LOG_INFOS += f"""{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The folder {REPLICA} is empty. The content from {SOURCE} was copied in {REPLICA}.\n"""

    #Create a list of all the subfolders in the source directory.
    source_folders_list = []
    for folder in source_paths_list:
        try:
            source_folders_list.append(re.search(r"{}\/(.+)".format(source_folder_name), folder)[1])
        except:
            pass

    #Create a list of all the subfolders in the replica directory.
    replica_folders_list = []
    for folder in replica_paths_list:
        try:
            replica_folders_list.append(re.search(r"{}\/(.+)".format(replica_folder_name), folder)[1])
        except:
            pass

    #Create a list of all the subfolders in the source directory that do not exist in the replica directory and create them.
    altered_folders = source_folders_list.copy()
    for source_folder in source_folders_list:
        for replica_folder in replica_folders_list:
            if source_folder == replica_folder:
                altered_folders.remove(replica_folder)
    for element in altered_folders:
        os.mkdir(os.path.join(REPLICA, element))
        LOG_INFOS += f"""{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The folder {element} could not be found and was created.\n"""

    #Create a list of all the subfolders in the replica directory that do not exist in the source directory and delete them.
    altered_folders = replica_folders_list.copy()
    for replica_folder in replica_folders_list:
        for source_folder in source_folders_list:
            if source_folder == replica_folder:
                altered_folders.remove(source_folder)
    for element in altered_folders:
        shutil.rmtree(os.path.join(REPLICA, element))
        LOG_INFOS += f"""{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The folder {element} was deleted from {REPLICA}.\n"""

    #Create a list of all the files in the source directory that do not exist in the replica directory and copy them.
    altered_files = source_files_infos.copy()
    for source_file in source_files_infos:
        for replica_file in replica_files_infos:
            if replica_file == source_file:
                altered_files.remove(replica_file)
    for element in altered_files:
        source_file_path = SOURCE + "/" + element['folder'] + "/" + element["filename"]
        replica_file_path = REPLICA + "/" + element['folder'] + "/" + element["filename"]
        shutil.copy(source_file_path, replica_file_path)
        LOG_INFOS += f"""{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The file {element["filename"]} was copied from {SOURCE + "/" + element['folder']}.\n"""

    #Create a list of all the files in the replica directory that do not exist in the source directory and delete them.
    altered_files = replica_files_infos.copy()
    for replica_file in replica_files_infos:
        for source_file in source_files_infos:
            if replica_file == source_file:
                altered_files.remove(source_file)
    for element in altered_files:
        try:
            replica_file_path = REPLICA + "/" + element['folder'] + "/" + element["filename"]
            os.remove(replica_file_path)
        except:
            pass
        LOG_INFOS += f"""{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: The file {element["filename"]} was removed from {REPLICA + "/" + element['folder']}.\n"""

    LOG_INFOS += f"""{dt.now().strftime('%d/%m/%Y')} at {dt.now().strftime('%H:%M:%S')}: End of log infos.\n"""

    print(LOG_INFOS)

    with open(log_file_path, 'w+') as f:
        f.write(LOG_INFOS)

backup_script()
schedule.every(BACKUP_SCHEDULE).minutes.do(backup_script)

# Loop so that the scheduling task keeps on running all time.
while True:
    # Checks whether a scheduled task is pending to run or not
    schedule.run_pending()
    time.sleep(1)
