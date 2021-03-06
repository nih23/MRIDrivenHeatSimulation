#/bin/bash

export SCAFESRUN_NAME_EXECUTABLE="a.out";
export SCAFESRUN_SPACE_DIM=3
export SCAFESRUN_TYPE_DOMAIN_DECOMPOSITION="UNI"
export SCAFESRUN_COORD_NODE_FIRST="0x0x0"
export SCAFESRUN_COORD_NODE_LAST="1x1x1"
export SCAFESRUN_N_TIMESTEPS=20
export SCAFESRUN_N_SNAPSHOTS=1
export SCAFESRUN_START_TIME=0
export SCAFESRUN_END_TIME=1
export SCAFESRUN_OUTPUT_LEVEL=5
export SCAFESRUN_NLAYERS_AT_BORDER=1
export SCAFESRUN_NAME_KINDFILE=""
export SCAFESRUN_WRITE_KINDFILE="NO";
export SCAFESRUN_NAME_CONFIGFILE=""
export SCAFESRUN_ENABLE_ADOLC="NO"
export SCAFESRUN_ASYNCHRON_MODE="YES"
export SCAFESRUN_COMP_GRADIENTS="NO"
export SCAFESRUN_RESULTS_DIR="./";
export SCAFESRUN_CHECK_RESULTS="YES";

#------------------------------------------------------------------------------#
#export SCAFESRUN_RUN_MODE="SLURM_WITH_SBATCH_CALL"
export SCAFESRUN_RUN_MODE="NORMAL"
export SCAFESRUN_N_TESTS_MPI=1;
export SCAFESRUN_N_TESTS_OPENMP=1;
export SCAFESRUN_TYPE_SCALINGTEST="STRONG"
export SCAFESRUN_MACHINE_NAME="ZIH_TAURUS2";
export SCAFESRUN_MACHINE_N_NODES=512;
export SCAFESRUN_MACHINE_N_CORES_PER_NODE=16;
