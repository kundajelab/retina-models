#!/bin/bash
set -e
set -o pipefail
set -u 

BASE=/scratch/users/surag/retina/
RUNNAME=20220202_bpnet
JOBSCRIPT=/home/users/surag/kundajelab/retina-models/jobscripts/jobscript.sh

mkdir -p $BASE/models/$RUNNAME/fold0/metrics

cd /home/users/surag/kundajelab/retina-models/src

for x in `ls $BASE/bigwigs`
 do
  n=$(basename -s ".bw" $x);
  sbatch --job-name metrics_$n \
         --output $BASE/models/$RUNNAME/fold0/logs/$n.metrics.log.txt \
         --error $BASE/models/$RUNNAME/fold0/logs/$n.metrics.err.txt \
         --mem 50G \
         --time 1:00:00 \
         $JOBSCRIPT metrics.py \
         --genome /scratch/users/surag/genomes/GRCh38_no_alt_analysis_set_GCA_000001405.15.fasta \
         --bigwig $BASE/bigwigs/$x \
         --peaks $BASE/peaks/peaks_3000/${n}_peakCalls_sorted.bed \
         --nonpeaks $BASE/peaks/gc_neg/${n}_peakCalls_sorted.gc.neg.bed \
         --output-prefix $BASE/models/$RUNNAME/fold0/metrics/$n \
         --model $BASE/models/$RUNNAME/fold0/saved/$n.h5 \
         --test-chr "chr1" "chr3" "chr6" 
 done
