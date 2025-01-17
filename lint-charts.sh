#!/usr/bin/env bash

#
# Script to Lint all charts
#

echo "Linting all Charts..."

set -e

LOCAL_HELM_MOJALOOP_REPO_URI=${HELM_MOJALOOP_REPO_URI:-'https://docs.mojaloop.io/helm/repo'}

trap 'echo "Command failed...exiting. Please fix me!"' ERR


if [ "$1" ]; then
    declare -a charts=("$1")
else
    declare -a charts=(
        example-mojaloop-backend
        ml-testing-toolkit
        ml-testing-toolkit-cli
        sdk-scheme-adapter/chart-service
        sdk-scheme-adapter
        mojaloop-ttk-simulators/chart-sim1
        mojaloop-ttk-simulators/chart-sim2
        mojaloop-ttk-simulators/chart-sim3
        mojaloop-ttk-simulators
        eventstreamprocessor
        simulator
        monitoring/promfana
        monitoring/efk
        account-lookup-service
        als-oracle-pathfinder
        centralkms
        # forensicloggingsidecar  # No longer supported
        centralledger
        # centralenduserregistry  # No longer supported
        centralsettlement
        emailnotifier
        centraleventprocessor
        central
        ml-api-adapter
        quoting-service
        finance-portal
        finance-portal-settlement-management
        transaction-requests-service
        bulk-centralledger/
        bulk-api-adapter/
        mojaloop-bulk/
        mojaloop-simulator
        mojaloop
        # kube-system/ntpd/ # No longer supported
        ml-operator
        thirdparty/chart-auth-svc
        thirdparty/chart-consent-oracle
        thirdparty/chart-tp-api-svc
    )
fi

echo "\n"

for chart in "${charts[@]}"
do
    echo "---=== Linting $chart ===---"
    helm lint $chart
done

echo "\
Chart linting completed.\n \
Ensure you check the output for any errors. \n \
Ignore any http errors when connecting to \"local\" chart repository.\n \
\n \
Happy Helming!
"
