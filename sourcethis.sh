#ln -s /home/htung/anaconda3/envs/py35 ~/Documents/install/blender-2.76b-linux-glibc211-x86_64/2.76/python
export BLENDER_SYSTEM_PYTHON=/home/htung/anaconda3/envs/py34
alias blender=~/Documents/install/blender-2.76b-linux-glibc211-x86_64/blender
export PYTHONPATH=$PWD:$PYTHONPATH
export BVP_SOURCE_DIR=$PWD
source activate py36-baselines