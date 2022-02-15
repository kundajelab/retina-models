#!/bin/bash
set -e
set -o pipefail
set -u 

BASE=/scratch/users/surag/retina/
RUNNAME=20220202_bpnet
JOBSCRIPT=/home/users/surag/kundajelab/retina-models/jobscripts/jobscript.sh

# make a copy of code run 
mkdir -p $BASE/models/$RUNNAME/fold0/interpret

cd /home/users/surag/kundajelab/retina-models/src

for x in `ls $BASE/bigwigs`
 do
  n=$(basename -s ".bw" $x);
  sbatch --job-name train_$n \
         --output $BASE/models/$RUNNAME/fold0/logs/$n.interpret.log.txt \
         --error $BASE/models/$RUNNAME/fold0/logs/$n.interpret.err.txt \
         --mem 100G \
         $JOBSCRIPT interpret.py \
         --genome /scratch/users/surag/genomes/GRCh38_no_alt_analysis_set_GCA_000001405.15.fasta \
         --model $BASE/models/$RUNNAME/fold0/saved/$n.h5 \
         --regions $BASE/peaks/peaks_3000/${n}_peakCalls_sorted.bed \
         --output-prefix $BASE/models/$RUNNAME/fold0/interpret/$n 
 done
