#!/bin/bash
set -e
set -o pipefail
set -u 

BASE=/scratch/users/surag/retina/
RUNNAME=20220202_bpnet
JOBSCRIPT=/home/users/surag/kundajelab/retina-models/jobscripts/jobscript.sh

# make a copy of code run 
mkdir -p $BASE/models/$RUNNAME/fold0/modisco

cd /home/users/surag/kundajelab/retina-models/src

for x in `ls $BASE/bigwigs`
 do
  n=$(basename -s ".bw" $x);
  mkdir -p $BASE/models/$RUNNAME/fold0/modisco/$n

  sbatch --job-name modisco_${n} \
         --output $BASE/models/$RUNNAME/fold0/logs/$n.modisco.log.txt \
         --error $BASE/models/$RUNNAME/fold0/logs/$n.modisco.err.txt \
         --mem 250G \
         --gres=gpu:0 \
         --time 48:00:00 \
         --partition owners,akundaje \
         $JOBSCRIPT run_modisco.py \
         --scores-prefix $BASE/models/$RUNNAME/fold0/interpret/$n \
         --profile-or-counts counts \
         --output-dir $BASE/models/$RUNNAME/fold0/modisco/$n \
         --max-seqlets 50000
 done
