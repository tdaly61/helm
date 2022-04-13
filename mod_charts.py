#!/usr/bin/env python3

"""
    various modifications and processing of helm charts especially  values.yaml files
    author: Tom Daly (tdaly61@gmail.com)
    Date : April 2022
"""

from operator import sub
import sys
import re
import argparse
import os 
from pathlib import Path
from shutil import copyfile 
import yaml
from fileinput import FileInput


def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Automate modifications across mojaloop helm charts')
    parser.add_argument("-d", "--directory", required=True, help="directory for helm charts")

    args = parser.parse_args(args)
    if len(sys.argv[1:])==0:
        parser.print_help()
        parser.exit()
    return args

##################################################
# main
##################################################
def main(argv) :
    args=parse_args()

    p = Path() / args.directory
    print(f"mypath: [{p}]")
    print(f"Processing helm charts in directory: [{args.directory}]")

    # walk the directory structure and process all the values.yaml files 
    # replace solsson kafka with kymeric
    
    for vf in p.rglob('**/values.yaml'):
        print(vf)
        backupfile= Path(vf.parent) / f"{vf.name}.bak"
        copyfile(vf, backupfile)
        with FileInput(files=[vf], inplace=True) as f:
            for line in f:
                line = line.rstrip()
                line = re.sub("repository:\s*solsson/kafka" , "repository: kymeric/cp-kafka ", line )
                print(line)

        


    l = list(p.glob('**/values.yaml'))
    #print(f"values files : [{l}]")

    # for i in range(len(l)) : 
    #     print(f"{'/n'.join(l)}")

    # y = p / 'central' / 'values.yaml'
    # with open(y) as f:
    #     newdct = yaml.load(f)
    #     # for item, doc in newdct.items():
    #     #     print(item, ":", doc)

    # print(yaml.dump(newdct))
    

if __name__ == "__main__":
    main(sys.argv[1:])
