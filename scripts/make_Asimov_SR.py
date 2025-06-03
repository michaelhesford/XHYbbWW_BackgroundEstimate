'''
For blinded fit. Grabs real ttbar measurement region data and signal region Asimov data and throws it into one root file which can be referenced in the 2DAlphabet json.
'''
from glob import glob
import subprocess, os
import ROOT
from collections import OrderedDict

file_ttCR = ROOT.TFile.Open('/uscms/home/mhesford/nobackup/XHYbbWW/CMSSW_12_3_5/src/semileptonic/selection/XHYbbWWselection_DataRun2.root','READ')
ttCR_hist = file_ttCR.Get('MXvMY_pass_ttCR__nominal')

file_SR = ROOT.TFile.Open('PseudoDataToy_Poisson_method_seed12345_unblindedFail.root','READ')
SR_hist = file_SR.Get('Asimov_pass_SR')
SR_hist.SetName('MXvMY_pass_SR__nominal')
SR_hist.SetTitle('MXvMY_pass_SR__nominal')

outFile = ROOT.TFile.Open('selection/Data_Asimov_fit.root','RECREATE')
outFile.cd()
ttCR_hist.Write()
SR_hist.Write()
