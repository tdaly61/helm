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
        - TEST out how good the high level charts are by making the changes only in the toplevel values.xml.  Yeah in theory I could have just done the 
          toplevel charts and done them by hand BUT I still need to modify the requirememts and add ghe local mysql,kafka and zookeepr charts AND 
          doing this coding starts a toolchain that we might use more in the future. 
        - OK I can probably do all this now with the ruamel yaml modules , but tidy it up later not now.
    
"""



from operator import sub
import sys
import re
import argparse
import os 
from pathlib import Path
from shutil import copyfile 
#import yaml
from fileinput import FileInput
from ruamel.yaml import YAML
from sqlalchemy import null

data = None

def print_debug(x1, x2, c=0) :  
    print("******************")
    print(f" [{c}]: {x1} " )
    print(f" [{c}]: {x2} " )
    print("******************")
                
def lookup(sk, d, path=[]):
   # lookup the values for key(s) sk return as list the tuple (path to the value, value)
   if isinstance(d, dict):
       for k, v in d.items():       
           if k == sk:
               yield (path + [k], v)
           for res in lookup(sk, v, path + [k]):
               yield res
   elif isinstance(d, list):
       for item in d:
           for res in lookup(sk, item, path + [item]):
               yield res

for path, value in lookup("nfs", data):
    print(path, '->', value)

# command
#
def update_key(key, value, dictionary):
        for k, v in dictionary.items():
            #print(f"printing k: {k} and printing key: {key} ")
            if k == key:
                #print("indeed k == key")
                dictionary[key]=value
                #print(f" the dictionary got updated in the previous line : {dictionary} ")
                #return []
            elif isinstance(v, dict):
                for result in update_key(key, value, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    if isinstance(d, dict):
                        for result in update_key(key, value, d):
                            yield result

def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Automate modifications across mojaloop helm charts')
    parser.add_argument("-d", "--directory", required=True, help="directory for helm charts")
    parser.add_argument("-v", "--values", required=False, action="store_true", help="modify only the values.yaml files")
    parser.add_argument("-r", "--requirements", required=False, action="store_true", help="modify only the requirements.yaml files")
    parser.add_argument("-t", "--testonly", required=False, action="store_true", help="run the test section of the code only ")
    parser.add_argument("-a", "--all", required=False, action="store_true", help="modify values and requirements yaml files")

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
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096

    # walk the directory structure and process all the values.yaml files 
    # replace solsson kafka with kymeric
    # replace kafa start up check with netcat test (TODO check to see if this is ok) 
    # replace mysql with arm version of mysql and adjust tag on the following line (TODO: check that latest docker mysql/mysql-server latest tag is ok )
    # TODO: maybe don't do this line by line but rather read in the entire file => can match across lines and avoid the next_line_logic 
    # for now disable metrics and metrics exporting
    # replace the mojaloop images with the locally built  ones

    if (  args.all or args.values  ) : 
        print("\n\n=============================================================")
        print("Processing values.yaml files.. ")
        print("=============================================================")
    
        for vf in p.rglob('*/values.yaml'):
            backupfile= Path(vf.parent) / f"{vf.name}_bak"
            print(f"{vf} : {backupfile}")
            copyfile(vf, backupfile)
            with FileInput(files=[vf], inplace=True) as f:
                next_line_is_mojaloop_tag = False
                for line in f:
                    line = line.rstrip()

                    # now update the mojaloop images 
                    if (next_line_is_mojaloop_tag):
                        line = re.sub("tag:.*$", "tag: latest", line )
                        next_line_is_mojaloop_tag = False
                    # TODO : check that there is no mojaloop image with > 3 parts to its name i.e. > 3 hypens
                    if re.match(r"(\s+)repository:\s*mojaloop", line ) : 
                        line = re.sub(r"(\s+)repository:\s*mojaloop/(\w+)-(\w+)-(\w+)-(\w+)", r"\1repository: \2_\3_\4_\5_local", line )
                        line = re.sub(r"(\s+)repository:\s*mojaloop/(\w+)-(\w+)-(\w+)", r"\1repository: \2_\3_\4_local", line )
                        line = re.sub(r"(\s+)repository:\s*mojaloop/(\w+)-(\w+)", r"\1repository: \2_\3_local", line )
                        line = re.sub(r"(\s+)repository:\s*mojaloop/(\w+)", r"\1repository: \2_local", line )
                        next_line_is_mojaloop_tag = True 

                    print(line)



    ## TODO  Need to modify the kafka requirements.yaml to update the zookeeper image 
    ##       if I am fully automating this 
    # walk the directory structure and process all the requirements.yaml files 
    # kafka => local kafka chart 
    # mysql/percona => local mysql chart with later arm64 based image 
    # zookeeper => local zookeeper (this is in the requirements.yaml of the kafka local chart)
    
    if (  args.all or args.requirements  ) : 
        print("\n\n=============================================================")
        print("Processing requirements.yaml files ")
        print("=============================================================")
        for rf in p.rglob('*/requirements.yaml'):
            backupfile= Path(rf.parent) / f"{rf.name}_bak"
            print(f"{rf} : {backupfile}")
            copyfile(rf, backupfile)
            with open(rf) as f:
                reqs_data = yaml.load(f)
                #print(reqs_data)
            try: 
                dlist = reqs_data['dependencies']
                for i in range(len(dlist)): 
                    if (dlist[i]['name'] == "percona-xtradb-cluster"): 
                        print(f"old was: {dlist[i]}")
                        dlist[i]['name'] = "mysql"
                        dlist[i]['version'] = "1.0.0"
                        dlist[i]['repository'] = "file://../mysql"
                        dlist[i]['alias'] = "mysql"
                        dlist[i]['condition'] = "enabled"
                        print(f"new is: {dlist[i]}")

                    if (dlist[i]['name'] == "kafka"):
                        print(f"old was: {dlist[i]}")
                        dlist[i]['repository'] = "file://../kafka"
                        dlist[i]['version'] = "1.0.0"
                        print(f"new is: {dlist[i]}")

                    if (dlist[i]['name'] == "zookeeper"):
                        print(f"old was: {dlist[i]}")
                        dlist[i]['version'] = "1.0.0"
                        dlist[i]['repository'] = "file://../zookeeper"
                        print(f"new is: {dlist[i]}")

                    if (dlist[i]['name'] == "mongodb"):
                        print(f"old was: {dlist[i]}")
                        dlist[i]['version'] = "1.0.0"
                        dlist[i]['repository'] = "file://../mongodb"
                        print(f"new is: {dlist[i]}")
            except Exception:
                continue 
            #print(yaml.dump(reqs_data))
            with open(rf, "w") as f:
                yaml.dump(reqs_data, f)
              
    if (  args.testonly ) : 
        print("\n\n===============================================================")
        print("running toms code tests")
        print(" at this stage trying to just modify the mojaloop/values.yaml file")
        print("===============================================================")
         
        # vf = p / "mojaloop" / "values.yaml"
        # backupfile = Path(vf.parent) / f"{vf.name}_bak1"
        # print (backupfile)
        # print(f"mojaloop values file : {vf.parent}/{vf.name}")
        # copyfile(vf, backupfile)

        for vf in p.rglob('centrall*/values.yaml'):
            backupfile= Path(vf.parent) / f"{vf.name}_bak"
            print(f"{vf} : {backupfile}")
            copyfile(vf, backupfile)
            
            with open(vf) as f:
                data = yaml.load(f)

            # update kafka settings 
            count = 0
            for x, value in lookup("kafka", data):    
                list(update_key('command', 'until nc -vz -w 1 $kafka_host $kafka_port; do echo waiting for Kafka; sleep 2; done;' , value))
                list(update_key('repository', 'kymeric/cp-kafka' , value))
                list(update_key('image', 'kymeric/cp-kafka' , value))
                list(update_key('imageTag', 'latest' , value))
                print_debug(x,value)

            # turn off promerthiues jmx and kafka exporter 
            for x, value in lookup("prometheus", data):
                print_debug(x,value , 2)
                if  isinstance(value, dict):
                    if value.get("jmx"): 
                        value['jmx']['enabled'] = False
                    if value.get("kafka"): 
                        value['kafka']['enabled'] = False
                    
        
            # update mysql settings 
            for x, value in lookup("mysql", data):  
                list(update_key('repository', 'mysql/mysql-server' , value))
                list(update_key('tag', '8.0.28-1.2.7-server' , value))
                # pos = list(mydict.keys()).index('Age')
                # items = list(mydict.items())
                # items.insert(pos, ('Phone', '123-456-7890'))
                if value.get("image") : 
                    del value['image']
                    value['image'] = "mysql/mysql-server"
                    value['imageTag'] = "8.0.28-1.2.7-server"
                    value['pullPolicy'] = "ifNotPresent"

            # turn the side car off for the moment 
            for x, value in lookup("sidecar", data):  
                list(update_key('enabled', 'False' , value))


            # turn metrics off 
            # The simulator has metrics clause with no enabled setting  => hence need to test
            for x, value in lookup("metrics", data):    
                try: 
                    if value.get("enabled") : 
                        value['enabled'] = False
                except Exception: 
                    continue            
            
            with open(vf, "w") as f:
                yaml.dump(data, f)

      
    
if __name__ == "__main__":
    main(sys.argv[1:])
