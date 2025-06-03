#!/bin/bash

# This script will make the tarball of the CMSSW environment with this custom 2DAlphabet. It will be used to generate the workspaces on condor in parallel, since doing it locally will take ages
WD=$(pwd)
cd $CMSSW_BASE/../
    tar --exclude-caches-all --exclude-vcs -cvzf CMSSW_14_1_0_pre4_env.tgz \
    --exclude=tmp --exclude=".scram" --exclude=".SCRAM" \
    --exclude=CMSSW_14_1_0_pre4/src/HiggsAnalysis/CombinedLimit/docs \
    --exclude=CMSSW_14_1_0_pre4/src/HiggsAnalysis/CombinedLimit/data/benchmarks \
    --exclude=CMSSW_14_1_0_pre4/src/HiggsAnalysis/CombinedLimit/data/tutorials \
    --exclude=CMSSW_14_1_0_pre4/src/XHYbbWW_BackgroundEstimate/*.png \
    --exclude=CMSSW_14_1_0_pre4/src/XHYbbWW_BackgroundEstimate/*.pdf \
    --exclude=CMSSW_14_1_0_pre4/src/XHYbbWW_BackgroundEstimate/limits_fall2024 \
    --exclude=CMSSW_14_1_0_pre4/src/XHYbbWW_BackgroundEstimate/logs \
    --exclude=CMSSW_14_1_0_pre4/src/XHYbbWW_BackgroundEstimate/QCDtrigStudies \
    --exclude=CMSSW_14_1_0_pre4/src/XHYbbWW_BackgroundEstimate/limits_2025-01-14 \
    --exclude=CMSSW_14_1_0_pre4/src/XHYbbWW_BackgroundEstimate/limits_fall2024 \
    --exclude=CMSSW_14_1_0_pre4/src/XHYbbWW_BackgroundEstimate/QCDrpf_fits \
    --exclude=CMSSW_14_1_0_pre4/src/twoD-env \
    CMSSW_14_1_0_pre4
xrdcp -f CMSSW_14_1_0_pre4_env.tgz root://cmseos.fnal.gov//store/user/$USER/
cd $CMSSW_BASE/src/XHYbbWW_BackgroundEstimate
