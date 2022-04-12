#!/usr/bin/env bash
# this script is testing to see how much of the work to implement ML on arm64 can be automated
# assumes ML repos are safely forked into a separate GitHub Repo and clonable to local environment 




function update_dockerfile {
    printf "Modifying Dockerfile [$1] \n"
    perl -i.bak-1 -pe 's/FROM \S+/FROM $ENV{DOCKER_BASE_IMAGE}/g' $1/Dockerfile
    perl -i.bak-2 -pe 's/python\s/python3 /g' $1/Dockerfile
}

function build_docker_image {
    printf "image for [$1] \n"
    build_image=${GIT_REPO_ARRAY[$1]}
    printf "building docker image [$build_image] \n"
    cd $WORKING_DIR; cd $1
    docker build --no-cache --platform linux/arm64/v8 -t $build_image .
    cd $WORKING_DIR
}

function convert_to_containerd_image {
    #TODO check docker image actually exists 
    #todo make sure microk8s in installed 
    #TODO : how does this work for k3s ? 
    printf "converting image [$1] \n"
    DOCKER_SAVE_FILE=/tmp/docker_save.tar
    rm -rf $DOCKER_SAVE_FILE
    build_image=${GIT_REPO_ARRAY[$1]}
    docker save $build_image > $DOCKER_SAVE_FILE
    microk8s ctr image import $DOCKER_SAVE_FILE  
}

################################################################################
# Function: showUsage
################################################################################
# Description:		Display usage message
# Arguments:		none
# Return values:	none
#
function showUsage {
	if [ $# -ne 0 ] ; then
		echo "Incorrect number of arguments passed to function $0"
		exit 1
	else
echo  "USAGE: $0 
Example 1 : do_arm64.sh -m all 

Options:
-m mode .............all|convert_images|update_charts
-h|H ............... display this message
"
	fi
}

################################################################################
# MAIN
################################################################################

##
# Environment Config
##
SCRIPTNAME=$0
WORKING_DIR=$HOME/work
HELM_CHARTS_DIR=$HOME/helm
SCRIPT_DIR="$( dirname "${BASH_SOURCE[0]}" )"
REPO_BASE=https://github.com/tdaly61
#REPO_LIST=(central-event-processor central-settlement central-ledger)
export DOCKER_BASE_IMAGE="arm64v8/node:12-alpine"
declare -A GIT_REPO_ARRAY=(
    [central-event-processor]=central_event_processor_local 
    [central-settlement]=central_settlement_local 
    [central-ledger]=central_ledger_local 
)
cd $WORKING_DIR
pwd

# if [ "$EUID" -ne 0 ]
#   then echo "Please run as root"
#   exit 1
# fi

# Check arguments
# if [ $# -lt 1 ] ; then
# 	showUsage
# 	echo "Not enough arguments -m mode must be specified "
# 	exit 1
# fi

# Process command line options as required
while getopts "m:t:u:v:rhH" OPTION ; do
   case "${OPTION}" in
        m)	mode="${OPTARG}"
        ;;
        h|H)	showUsage
                exit 0
        ;;
        *)	echo  "unknown option"
                showUsage
                exit 1
        ;;
    esac
done

printf "\n\n*** Mojaloop -  building arm images and helm charts ***\n\n"
 
# node is just a place holder flag right now. 
if [[ "$mode" == "all" ]]  ; then
	printf " running arm updating of ML \n\n"

    for key in  ${!GIT_REPO_ARRAY[@]}; do
        if [ ! -d $key ]; then
            printf "cloning repo: [$REPO_BASE/$key.git] \n"
            #git clone $REPO_BASE/$key.git 
        else 
            printf "repo: [$REPO_BASE/$key.git]  already exists ..skipping clone\n"        
        fi    
    done 

    printf "\n========================================================================================\n"
    printf "Modifying Dockerfiles \n"
    printf "========================================================================================\n"
    for key in  ${!GIT_REPO_ARRAY[@]}; do
        update_dockerfile $key
    done 

    printf "\n========================================================================================\n"
    printf " Building docker images \n"
    printf "========================================================================================\n"
    
    for key in  ${!GIT_REPO_ARRAY[@]}; do
        #build_docker_image $key
        printf "skipping build_docker_image $key\n"
    done     

fi 

if [[ "$mode" == "convert_images" ]]  ; then
    printf "\n========================================================================================\n"
    printf " Converting docker images to containerd (cri) \n"
    printf "========================================================================================\n"
    for key in  ${!GIT_REPO_ARRAY[@]}; do
        convert_to_containerd_image $key
    done     
fi 

if [[ "$mode" == "update_charts ]]  ; then
    printf "\n========================================================================================\n"
    printf " Updating helm charts to use correct images \n"
    printf "========================================================================================\n"
    for key in  ${!GIT_REPO_ARRAY[@]}; do
        convert_to_containerd_image $key
    done     
fi 
