#Author:Elin
#Create Time:2024-01-19 13:39:25
#Last Modified By:Elin
#Update Time:2024-01-19 13:39:25
#**coding:utf-8**

import sys
import os
import pathlib
from prettytable import PrettyTable
from pydantic import BaseModel
from argparse import ArgumentParser
from datetime import datetime,timezone,timedelta
import pwd
import time

__VERSION__ = "0.0.1"
__TIMEZONE__ = timezone(timedelta(seconds=-time.altzone if time.localtime().tm_isdst else -time.timezone))


class RecursObjectDescription(BaseModel):
    name:str
    type:str
    size:str
    permission:str
    owner:str
    lastModified:str
def FormatDestinationSize(size:float):
    if size < 1024:
        return str(size) + "B"
    elif size >= 1024 and size < 1024 * 1024:
        return str(round(size / 1024,2)) + "KB"
    elif size >= 1024 * 1024 and size < 1024 * 1024 * 1024:
        return str(round(size / 1024 / 1024,2)) + "MB"
    elif size >= 1024 * 1024 * 1024 and size < 1024 * 1024 * 1024 * 1024:
        return str(round(size / 1024 / 1024 / 1024,2)) + "GB"
    elif size >= 1024 * 1024 * 1024 * 1024 and size < 1024 * 1024 * 1024 * 1024 * 1024:
        return str(round(size / 1024 / 1024 / 1024 / 1024,2)) + "TB"
    else:
        return "Over the bound."
def PathRecurs(path:str):
    if pathlib.Path(path).is_dir() != True and pathlib.Path(path).exists() != True:
        return "Invalid path from terminal given,make sure it exists on fs or valid path."
    else:
        RecurseResult = []
        for root,dirs,files in os.walk(path):
            for file in files:
                try:
                    file_path = os.path.join(root,file)
                    file_size = FormatDestinationSize(os.path.getsize(file_path))
                    file_permission = oct(os.stat(file_path).st_mode)[-4:]
                    # Determine file type 
                    if os.path.islink(file_path):
                        file_type = "link"
                    else:
                        file_type = "file"
                    # Get object owner
                    file_owner = pwd.getpwuid(os.stat(file_path).st_uid).pw_name
                    # Set into CST timezone
                    file_lastModified = datetime.utcfromtimestamp(os.stat(file_path).st_mtime)
                    # Get local time
                    file_lastModified = file_lastModified.replace(tzinfo=timezone.utc).astimezone(__TIMEZONE__).strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(str(e))
                    file_path = os.path.join(root,file)
                    file_size = "Unaccessible"
                    file_permission = "Unaccessible"
                    file_type = "Unaccessible"
                    file_owner = "Unaccessible"
                    file_lastModified = "Unaccessible"
                RecurseResult.append(RecursObjectDescription(name=file,type=file_type,size=file_size,permission=file_permission,owner=file_owner,lastModified=file_lastModified))
            for dir in dirs:
                try:
                    dir_path = os.path.join(root,dir)
                    dir_size = FormatDestinationSize(os.path.getsize(dir_path))
                    dir_permission = oct(os.stat(dir_path).st_mode)[-3:]
                    dir_type = "dir"
                    dir_owner = pwd.getpwuid(os.stat(dir_path).st_uid).pw_name
                    dir_lastModified = datetime.utcfromtimestamp(os.stat(dir_path).st_mtime)
                    dir_lastModified = dir_lastModified.replace(tzinfo=timezone.utc).astimezone(__TIMEZONE__).strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(str(e))
                    dir_path = os.path.join(root,dir)
                    dir_size = "Unaccessible"
                    dir_permission = "Unaccessible"
                    dir_type = "Unaccessible"
                    dir_owner = "Unaccessible"
                    dir_lastModified = "Unaccessible"
                RecurseResult.append(RecursObjectDescription(name=dir,type=dir_type,size=dir_size,permission=dir_permission,owner=dir_owner,lastModified=dir_lastModified))
        return RecurseResult

def GetTable(RecurseResult:list,filteredFileType:str):
    filteredTable = PrettyTable()
    normalTable = PrettyTable()
    filteredTable.field_names = ["Name","Type","Size","Permission","Owner","Last Modified"]
    normalTable.field_names = ["Name","Type","Size","Permission","Owner","Last Modified"]
    for item in RecurseResult:
        if filteredFileType != None:
            if filteredFileType in item.name:
                filteredTable.add_row([item.name,item.type,item.size,item.permission,item.owner,item.lastModified])
        else:
            normalTable.add_row([item.name,item.type,item.size,item.permission,item.owner,item.lastModified])
    if filteredFileType != None:
        return len(filteredTable._rows),filteredTable
    else:
        return len(normalTable._rows),normalTable


def main():
    parser = ArgumentParser(description="A simple tool to recurs path and render result as table.")
    parser.add_argument("-v","--version",action="version",version="%(prog)s {}".format(__VERSION__))
    parser.add_argument("-p","--path",type=str,help="Path to recurs.")
    parser.add_argument("-f","--filter",type=str,help="Filter specific file type.")
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
    if args.path:
        RecurseResult = PathRecurs(args.path)
        if RecurseResult:
            if args.filter :
                try:
                    assert args.filter != "" and "." in args.filter
                except AssertionError:
                    print("Invalid filtered file type given.")
                    sys.exit(1)
                count,table = GetTable(RecurseResult,args.filter)
                
            else:
                count,table = GetTable(RecurseResult,None)
            print("Total {} items found.".format(count))
            print(table)
            sys.exit(0)
        else:
            print("No result found,maybe destination path permission denied or empty.")
            sys.exit(1)
    else:
        print("No path given,at least need 1 valid path.")
        sys.exit(1)
    

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Recur has encountered an error like below:\n{}".format(str(e)))
        sys.exit(1)