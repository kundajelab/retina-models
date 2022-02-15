#!/bin/bash
set -e
set -o pipefail
set -u

# Converts a set of bams to + and - strand 5' end bigwigs used for training BPNet

# make sure to give a prefix, final files are named ${OUTPREFIX}.bw
OUTPREFIX=$1  # e.g. /path/to/dir/prefix
REFCHROMSZ=$2 # e.g. /path/to/genome.sizes.txt
INFRAG=$3 # frag file

if ! [ -x "$(command -v bedtools)" ] ; then
    echo "Bedtools not found" >&2
    exit 1
fi

if ! [ -x "$(command -v bedGraphToBigWig)" ] ; then
    echo "bedGraphToBigWig not found" >&2
    exit 1
fi

printf "Making BedGraphs\n"
# tagAlign -> bedGraph
# genomecov documentation mentions only need to sort by chromosome
# remove non standard chrs
# shift "-" by +1 to make it +4/-4 instead of +4/-5
bedtools genomecov -5 -bg -g $REFCHROMSZ -i <(cat $INFRAG | grep "chr" | awk -v OFS='\t' '{print $1,$2,$2+1,"N",1000,"+"; print $1,$3,$3+1,"N",1000,"-"}' | sort -k1,1) | sort -k1,1 -k2,2n  > ${OUTPREFIX}.bedGraph

printf "Making BigWigs\n"
# bedGraph -> BigWig
bedGraphToBigWig ${OUTPREFIX}.bedGraph $REFCHROMSZ ${OUTPREFIX}.bw

# remove intermediates
rm ${OUTPREFIX}.bedGraph
