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
    
        for vf in p.rglob('central*/values.yaml'):
            backupfile= Path(vf.parent) / f"{vf.name}_bak"
            print(f"{vf} : {backupfile}")
            copyfile(vf, backupfile)
            with FileInput(files=[vf], inplace=True) as f:
                #next_line_is_mysql_tag = False
                #next_line_is_metrics_enabled = False
                next_line_is_mojaloop_tag = False
                for line in f:
                    line = line.rstrip()
                    # line = re.sub("repository:\s*solsson/kafka" , "repository: kymeric/cp-kafka ", line )
                    # #line = re.sub("./bin/kafka-broker-api-versions.sh --bootstrap-server", " nc -vz -w 1", line) 
                    # if (next_line_is_mysql_tag):
                    #     line = re.sub("tag:.*$", "tag: 8.0.28-1.2.7-server", line )
                    #     next_line_is_mysql_tag = False
                    # if re.match("\s*repository:\s*mysql", line ) : 
                    #     # modify to use the mysql-sever image for which there are arm builds
                    #     # and set flag to indicate next line is the tage which also needs updating 
                    #     line = re.sub("repository:\s*mysql", "repository: mysql/mysql-server", line )
                    #     next_line_is_mysql_tag=True 
                    
                    # # remove percona replace with mysql-server and latest tag, similar to above
                    # if re.match("\s*repository:.*percona", line ) : 
                    #   line = re.sub("repository:.*percona.*$", "repository: mysql/mysql-server", line )
                    #   next_line_is_mysql_tag=True 

                    # for now turn metrics off and metrics exporting off 
                    # if (next_line_is_metrics_enabled ):
                    #     if re.match("\s* #", line ):
                    #         continue
                    #     line = re.sub("enabled:.*$", "enabled: false", line )
                    #     next_line_is_metrics_enabled = False
                    # if re.match("\s*metrics.*$", line ) : 
                    #     next_line_is_metrics_enabled=True 
                    

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


        print("Still Processing values.yaml files.. ")
        for rf in p.rglob('central*/values.yaml'):
            backupfile= Path(rf.parent) / f"{rf.name}_bak1"
            print(f"{rf} : {backupfile}")
            copyfile(rf, backupfile)
            with open(rf) as f:
                reqs_data = yaml.load(f)
                #print(reqs_data)

            for x, y in reqs_data.items():
                print("===================================================================")
                print(x)
                # correct image for Kafka
                #print(f"{y}\n")
                if x == 'kafka':
                    print("foubd kafka ok")
                #   print(f"TOP POS{list(reqs_data.keys()).index(x)}")
                #   print(f"Current POS{list(y.keys()).index('enabled')}")
                # pos = list(mydict.keys()).index('Age')
                # items = list(mydict.items())
                # items.insert(pos, ('Phone', '123-456-7890'))
                    try : 
                        y['image'] = "kymeric/cp-kafka"
                        y['imageTag'] = "latest"
                        y['prometheus']['jmx']['enabled'] = False
                    except KeyError as ex:
                        continue

                # Set the correct mysql images
                # note this takes a little different format because I am using the local mysql chart with 
                # slightly different format
                # TODO: How do I put this image clauses BACK at the top of the myswl section
                # TODO: How do I add comments and beautify the code again 
                if x == 'mysql':
                    #print(y['image'])
                    try: 
                        del y['image']
                        # add back in the image details (note this goes to the bottom on the section)
                        y['image'] = "mysql/mysql-server"
                        y['imageTag'] = "8.0.28-1.2.7-server"
                        y['pullPolicy'] = "ifNotPresent"
                    except KeyError as ex:
                            print(f"Key error with : {x} ")
                            continue

                #for the moment set all the sidecars to false
                if type(y) is dict : 
                    if y.get("sidecar") : 
                        y['sidecar']['enabled'] = False

                # check one level of nesting deeper for kafka resources 
                if type(y) is dict : 
                    if y.get('init', {}).get('kafka') : 
                        #print("found kafka")
                        #print(y['init']['kafka']['command'])
                        y['init']['kafka']['command'] = "until nc -vz -w 1 $kafka_host $kafka_port; do echo waiting for Kafka; sleep 2; done;"


            with open(rf, "w") as f:
                yaml.dump(reqs_data, f)    
    
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
        for rf in p.rglob('central*/requirements.yaml'):
            backupfile= Path(rf.parent) / f"{rf.name}_bak"
            print(f"{rf} : {backupfile}")
            copyfile(rf, backupfile)
            with open(rf) as f:
                reqs_data = yaml.load(f)
                #print(reqs_data)

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

            #print(yaml.dump(reqs_data))
            with open(rf, "w") as f:
                yaml.dump(reqs_data, f)
              
    if (  args.testonly ) : 
        print("\n\n===============================================================")
        print("running toms code tests")
        print(" at this stage trying to just modify the mojaloop/values.yaml file")
        print("===============================================================")
         
        mlfile = p / "mojaloop" / "values.yaml"
        backupfile = Path(mlfile.parent) / f"{mlfile.name}_bak1"
        print (backupfile)
        print(f"mojaloop values file : {mlfile.parent}/{mlfile.name}")
        copyfile(mlfile, backupfile)

        lev1_list=[]
        # get all the top level resources
        # with FileInput(files=[mlfile] ) as f:
        #     for line in f:
        #         line = line.rstrip()
        #         if re.match("^(\w+)", line ) : 
        #             #print(line)
        #             #print("*******************************************************************")
        #             line=line.rstrip(':')
        #             lev1_list.append(line)
        
        with open(mlfile) as f:
            data = yaml.load(f)

        #data['central']['centralledger']['centralledger-handler-transfer-prepare']['init']['kafka']['command'] = "tomxxxxx"
        #print(f"data just updated is {data['central']['centralledger']['centralledger-handler-transfer-prepare']['init']['kafka']['command']}")
        sample=0

        # update kafka settings 
        for x, value in lookup("kafka", data):    
            list(update_key('command', 'until nc -vz -w 1 $kafka_host $kafka_port; do echo waiting for Kafka; sleep 2; done;' , value))
            list(update_key('repository', 'kymeric/cp-kafka' , value))

        
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
            print("******************")
            print(x)
            print(value)
            print("******************")

        # turn metrics off 
        # The simulator has metrics clause with no enabled => hence need to test
        for x, value in lookup("metrics", data):    
            try: 
                if value.get("enabled") : 
                    value['enabled'] = False
            except Exception: 
                continue            

            #list(update_key('enabled', 'False' , value))
            

            # for k, v in value.items() :
            #     print("&&&&&&&&")
            #     print(k)
            #     print(v)
            #     print("&&&&&&&&")
        
        with open(mlfile, "w") as f:
            yaml.dump(data, f)

        # sample = 0 
        # for x, value in lookup("command", data):
        #     print("******************")
        #     print(x)
        #     print(value)
        #     print("******************")
        #     sample += 1
        #     if sample > 10 :
        #         break


if __name__ == "__main__":
    main(sys.argv[1:])
