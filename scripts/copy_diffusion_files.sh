#!/bin/bash

# copy nifti, bvec, and bval files to a common output directory and base name
# print final output nifti filename

set -e

inputnii=$1
inputbvec=$2
inputbval=$3
outputbase=$4

outdir=$(dirname $outputbase)
if [ ! -d "${outdir}" ]; then
  mkdir -p "${outdir}"
fi

$FSLDIR/bin/imcp ${inputnii} ${outputbase}
cp -f ${inputbvec} ${outputbase}.bvec
cp -f ${inputbval} ${outputbase}.bval

imglob -extension "${outputbase}"
