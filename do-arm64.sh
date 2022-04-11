#!/usr/bin/env bash
# this script is testing to see how much of the work to implement ML on arm64 can be automated
# assumes ML repos are safely forked into a separate GitHub Repo and clonable to local environment 




function update_dockerfile {
  printf "Modifying Dockerfile [$1] \n"
  pwd
  perl -i.bak -pe 's/FROM \S+/FROM $ENV{DOCKER_BASE_IMAGE}/g' $r/Dockerfile
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
Example 1 : do_arm64.sh -m arm 

Options:
-m mode .............do arm64 update of mojaloop 
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
SCRIPT_DIR="$( dirname "${BASH_SOURCE[0]}" )"
REPO_BASE=https://github.com/tdaly61
REPO_LIST=(central-event-processor central-settlement)
export DOCKER_BASE_IMAGE="arm64v8/node:12-alpine"

# printf "$DIR\n"
# printf "$BASE_DIR\n"
# printf "$SCRIPT_DIR\n"
cd $SCRIPT_DIR
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
if [[ "$mode" == "arm" ]]  ; then
	printf " running arm updating of ML \n\n"

    for r in  ${REPO_LIST[@]}; do
        if [ ! -d $r ]; then
            printf "cloning repo: [$REPO_BASE/$r.git] \n"
            git clone $REPO_BASE/$r.git 
        else 
            printf "repo: [$REPO_BASE/$r.git]  already exists ..skipping clone\n"        
        fi    
    done 

    printf "\n========================================================================================\n"
    printf "Modifying Dockerfiles \n"
    printf "========================================================================================\n"
    for r in  ${REPO_LIST[@]}; do
        update_dockerfile $r
    done 

fi 

