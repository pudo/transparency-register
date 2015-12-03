#!/bin/bash

ARCHIVE=$DATA_PATH/transparency-register
REGISTER=$ARCHIVE/register-`date +%Y%m%d`.xml
ACCREDITATIONS=$ARCHIVE/accreditations-`date +%Y%m%d`.xml

mkdir -p $ARCHIVE
curl -o $REGISTER "http://ec.europa.eu/transparencyregister/public/consultation/statistics.do?action=getLobbyistsXml&fileType=NEW"
curl -o $ACCREDITATIONS "http://ec.europa.eu/transparencyregister/public/consultation/statistics.do?action=getLobbyistsXml&fileType=ACCREDITED_PERSONS" 

echo "Uploading to S3..."
aws s3 cp $REGISTER s3://archive.pudo.org/transparency-register/register-`date +%Y%m%d`.xml
aws s3 cp $REGISTER s3://archive.pudo.org/transparency-register/register-latest.xml
aws s3 cp $ACCREDITATIONS s3://archive.pudo.org/transparency-register/accreditations-`date +%Y%m%d`.xml
aws s3 cp $ACCREDITATIONS s3://archive.pudo.org/transparency-register/accreditations-latest.xml

python scraper_register.py $REGISTER
python scraper_accreditations.py $ACCREDITATIONS

rm $REGISTER
rm $ACCREDITATIONS

