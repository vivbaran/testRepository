#!/bin/bash

#Environment settings
DB_URL=${1:-'localhost:3306'}
DB_USERNAME=${2:-'root'}
DB_PWD=${3:-'root'}
DB_NAME=${4:-'dev'}
STAGE=${5:-'dev'}

#clean up
rm -rf target/dist/adyaapp &> /dev/null
mkdir target &> /dev/null
mkdir target/dist &> /dev/null
mkdir target/dist/adyaapp &> /dev/null
mkdir target/dist/adyaapp/common &> /dev/null
mkdir target/dist/adyaapp/google &> /dev/null

cp -r adya target/dist/adyaapp/common
cp -r lib/lib/python2.7/site-packages/* target/dist/adyaapp/common

cp -r adya target/dist/adyaapp/google
cp -r lib/lib/python2.7/site-packages/* target/dist/adyaapp/google

cp common-serverless.yml target/dist/adyaapp/common/serverless.yml
cp google-serverless.yml target/dist/adyaapp/google/serverless.yml

cd target/dist/adyaapp/common

sls create_domain --stage=$STAGE
sls deploy --DB_URL=$DB_URL --DB_USERNAME=$DB_USERNAME --DB_PWD=$DB_PWD --DB_NAME=$DB_NAME --stage=$STAGE

cd ../google

sls deploy --DB_URL=$DB_URL --DB_USERNAME=$DB_USERNAME --DB_PWD=$DB_PWD --DB_NAME=$DB_NAME --stage=$STAGE