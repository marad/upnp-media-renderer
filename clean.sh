#!/bin/bash

DIRNAME=`dirname $0`

echo -n "Cleaning directory: $DIRNAME..."

find $DIRNAME -iname '*pyc' | xargs rm 2&> /dev/null
find $DIRNAME -iname '*~' | xargs rm 2&> /dev/null

echo "OK"