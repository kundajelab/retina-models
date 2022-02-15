#!/bin/bash
set -e
set -o pipefail
set -u 

BASE=/scratch/users/surag/retina/
RUNNAME=20220202_bpnet
JOBSCRIPT=/home/users/surag/kundajelab/retina-models/jobscripts/jobscript.sh


# make a copy of code run 
mkdir -p $BASE/models/$RUNNAME/fold2/logs
mkdir -p $BASE/models/$RUNNAME/fold2/saved
cp -r /home/users/surag/kundajelab/retina-models/src $BASE/models/$RUNNAME/fold2/code

cd /home/users/surag/kundajelab/retina-models/src

for x in `ls $BASE/bigwigs`
 do
  n=$(basename -s ".bw" $x);
  sbatch --job-name train_$n \
         --output $BASE/models/$RUNNAME/fold2/logs/$n.log.txt \
         --error $BASE/models/$RUNNAME/fold2/logs/$n.err.txt \
         --mem 100G \
         $JOBSCRIPT train.py \
         --genome /scratch/users/surag/genomes/GRCh38_no_alt_analysis_set_GCA_000001405.15.fasta \
         --bigwig $BASE/bigwigs/$x \
         --peaks $BASE/peaks/peaks_3000/${n}_peakCalls_sorted.bed \
         --nonpeaks $BASE/peaks/gc_neg/${n}_peakCalls_sorted.gc.neg.bed \
         --output-prefix $BASE/models/$RUNNAME/fold2/saved/$n \
         --test-chr "chr4" "chr11" "chr12" "chr15" "chrY" --val-chr "chr22" "chr7" \
         --max-jitter 500 
 done