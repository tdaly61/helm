#!/usr/bin/env bash
# get a list of all the github mojaloop rerpos so I can search em

USER=tdaly61@gmail.com
#curl -u $USER https://api.github.com/orgs/:your_organization/repos?type=private
#curl -v -H "Authorization: token $TOKEN"  https://api.github.com/orgs/mojaloop/repos?type=all
curl -v -H "Authorization: token $TOKEN"  https://api.github.com/orgs/mojaloop/repos?type=all?per_page=500
#curl -v -H "Authorization: token $TOKEN"  https://github.com/orgs/mojaloop/repositories?q=&type=all&language=&sort=name

#curl -v -H "Authorization: token 804ef78pretendtoken8762" -X POST https://api.github.com/users/lornajane/gists --data @github2.json
