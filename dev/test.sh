#!/bin/bash
# if run with $1, i assume that it being run from "dev" dir otherwise i need a REL path to zensearch in $1
if [[ ${1} ]]
then 
    REL=$1
else
    REL='..'
fi

pytest \
-vvv \
--verbose \
--cov=$REL/zensearch $REL/tests \
--cov-report term-missing:skip-covered