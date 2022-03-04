#!/bin/bash
set -e
set -o pipefail
set -u 

BASE=/scratch/users/surag/retina/
RUNNAME=20220202_bpnet
JOBSCRIPT=/home/users/surag/kundajelab/retina-models/jobscripts/jobscript.sh

cd /home/users/surag/kundajelab/retina-models/scripts

mkdir -p $BASE/models/$RUNNAME/fold0/interpret_bigwigs

for x in `ls $BASE/bigwigs`
 do
  n=$(basename -s ".bw" $x);
  sbatch --job-name h5_to_bw_${n} \
         --output $BASE/models/$RUNNAME/fold0/logs/$n.h5_to_bw.log.txt \
         --error $BASE/models/$RUNNAME/fold0/logs/$n.h5_to_bw.err.txt \
         --mem 40G \
         --time 2:00:00 \
         --gres gpu:0 \
         --partition akundaje,owners \
         $JOBSCRIPT /home/users/surag/kundajelab/retina-models/scripts/importance_hdf5_to_bigwig.py  \
         -h5 $BASE/models/$RUNNAME/fold0/interpret/${n}.counts_scores.h5 \
         -r $BASE/models/$RUNNAME/fold0/interpret/${n}.interpreted_regions.bed \
         -c /scratch/users/surag/genomes/GRCh38_no_alt_analysis_set_GCA_000001405.15.fasta.sizes \
         -o $BASE/models/$RUNNAME/fold0/interpret_bigwigs/$n.counts.importance.bw \
         -s $BASE/models/$RUNNAME/fold0/interpret_bigwigs/$n.counts.importance.stats.txt
 done
