#!/bin/bash

#SBATCH --job-name=btmh5
#SBATCH --output=/home/users/surag/CS273B/model_zoo/stage1/log.txt
#SBATCH --error=/home/users/surag/CS273B/model_zoo/stage1/err.txt
#SBATCH --time=48:00:00

#SBATCH --partition=gpu,akundaje

#SBATCH --nodes=1

#SBATCH --mem=52G

#SBATCH --gres=gpu:1

#SBATCH --cores-per-socket=8

module load cuda/11.2.0 
module load  cudnn/8.1.1.33

# https://stackoverflow.com/questions/34534513/calling-conda-source-activate-from-bash-script
eval "$(conda shell.bash hook)"
conda activate retina-multiome

echo "Live"
python "$@"
