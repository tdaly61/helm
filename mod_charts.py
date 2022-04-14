#!/usr/bin/env python3

"""
    various modifications and processing of helm charts especially  values.yaml files
    author: Tom Daly (tdaly61@gmail.com)
    Date : April 2022
    Notes : the main benefits of this programatic approach are : -
        - clearly documents the changes made to get the hel charts to work
        - starts building some tools that may well help to automate and simplify the maintence of the helm charts at
          least it enables investigation of that possibility. 
        - did this in python rather than perl one-lines because we need more control to match across lines 
          and because my perl programming is rather rusty. 
        - Also it looks like this approach could be used to modify ML V13.1 charts to run on K8s > v1.20 

    TODO: 
        - Should this be using PyYaml for the matching not regexp 
          (I looked at this but he helm charts are so long and nested it is ugly and hard , still perhaps another look is warranted)
        - Explore changing the helm charts and ingress to support ML > v1.20
    
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

    # charts_dict= { 
    #     "central-event-processor" : "central_event_processor_local",
    #     "central-settlement" : "central_settlement_local" ,
    #     "central-ledger" : "central_ledger_local" ,
    # }

    p = Path() / args.directory
    print(f"Processing helm charts in directory: [{args.directory}]")

    # walk the directory structure and process all the values.yaml files 
    # replace solsson kafka with kymeric
    # replace kafa start up check with netcat test (TODO check to see if this is ok) 
    # replace mysql with arm version of mysql and adjust tag on the following line (TODO: check that latest docker mysql/mysql-server latest tag is ok )
    # TODO: maybe don't do this line by line but rather read in the entire file => can match across lines and avoid the next_line_logic 
    # for now disable metrics and metrics exporting
    # replace the mojaloop images with the locally built  ones

    for vf in p.rglob('**/values.yaml'):
        backupfile= Path(vf.parent) / f"{vf.name}_bak"
        #backupfile= Path("/tmp") / f"{vf.name}.bak"
        print(f"{vf} : {backupfile}")
        copyfile(vf, backupfile)
        with FileInput(files=[vf], inplace=True) as f:
            next_line_is_mysql_tag = False
            next_line_is_metrics_enabled = False
            for line in f:
                line = line.rstrip()
                line = re.sub("repository:\s*solsson/kafka" , "repository: kymeric/cp-kafka ", line )
                line = re.sub("bin/kafka-broker-api-versions.sh --bootstrap-server", "nc -vz -w 1", line) 
                if (next_line_is_mysql_tag):
                    line = re.sub("tag:.*$", "tag: latest", line )
                    #line = line + '\ntomlatest'
                    next_line_is_mysql_tag = False
                if re.match("\s*repository:\s*mysql", line ) : 
                    # modify to use the mysql-sever image for which there are arm builds
                    # and set flag to indicate next line is the tage which also needs updating 
                    line = re.sub("repository:\s*mysql", "repository: mysql/mysql-server", line )
                    # line = line + '\ntomlaok'
                    next_line_is_mysql_tag=True 
                
                # for now turn metrics off and metrics exporting off 
                if (next_line_is_metrics_enabled ):
                    if re.match("\s* #", line ):
                        continue
                    line = re.sub("enabled:.*$", "enabled: false", line )
                    next_line_is_metrics_enabled = False
                if re.match("\s*metrics.*$", line ) : 
                    next_line_is_metrics_enabled=True 
                
                # now update the mojaloop images 
                # TODO : check that there is no mojaloop image with > 3 parts to its name i.e. > 3 hypens
                line = re.sub(r"\s*repository:\s*mojaloop/(\w+)-(\w+)-(\w+)", r"repository: \1_\2_\3_local mojatom ", line )
                line = re.sub(r"\s*repository:\s*mojaloop/(\w+)-(\w+)", r"repository: \1_\2_local mojatom ", line )
                line = re.sub(r"\s*repository:\s*mojaloop/(\w+)", r"repository: \1_local mojatom ", line )


                print(line)

        
    ## TODO  Need to modify the kafka requirements.yaml to update the zookeeper image 
    ##       if I am fully automating this 



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
