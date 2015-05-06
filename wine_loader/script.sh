#!/bin/sh
echo $(winepath $1) $2
../asc-qt $(winepath $1) $2
