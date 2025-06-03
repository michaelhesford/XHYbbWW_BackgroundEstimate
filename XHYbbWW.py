from time import time
from TwoDAlphabet import plot
from TwoDAlphabet.twoDalphabet import MakeCard, TwoDAlphabet
from TwoDAlphabet.alphawrap import BinnedDistribution, ParametricFunction
from TwoDAlphabet.helpers import make_env_tarball, cd, execute_cmd
from TwoDAlphabet.ftest import FstatCalc
import os
import numpy as np

def _get_other_region_names(pass_reg_name):
    return pass_reg_name,pass_reg_name.replace('pass','fail')

def _select_signal(row, args):
    signame = args[0]
    poly_order = args[1]
    if row.process_type == 'SIGNAL':
        if signame in row.process:
            return True
        else:
            return False
    elif 'Background' in row.process:
        if row.process == 'Background_'+poly_order:
            return True
        elif row.process == 'Background':
            return True
        else:
            return False
    else:
        return True
#------------------------------------------------------------------------------------------------------------
# NEED TO ADJUST THIS FUNCTION
#------------------------------------------------------------------------------------------------------------
def _load_CR_rpf(poly_order):
    twoD_CRonly = TwoDAlphabet('XHYfits_CR','XHYbbWW.json', loadPrevious=True)
    params_to_set = twoD_CRonly.GetParamsOnMatch('rpf.*'+poly_order, 'XHY-1000-500_area', 'b')
    return {k:v['val'] for k,v in params_to_set.items()}
#------------------------------------------------------------------------------------------------------------

def _load_CR_rpf_as_SR(poly_order):
    params_to_set = {}
    for k,v in _load_CR_rpf(poly_order).items():
        params_to_set[k.replace('CR','SR')] = v
    return params_to_set

def _generate_constraints(nparams):
    out = {}
    for i in range(nparams):
        if i == 0:
            out[i] = {"MIN":0,"MAX":2,"NOM":1}
        else:
            out[i] = {"MIN":-100,"MAX":100,"NOM":0}
    return out

_rpf_options = {
    '0x0': {
        'form': '0.1*(@0)',
        'constraints': _generate_constraints(1)
    },
    '1x0': {
        'form': '0.1*(@0+@1*x)',
        'constraints': _generate_constraints(2)
    },
    '0x1': {
        'form': '0.1*(@0+@1*y)',
        'constraints': _generate_constraints(2)
    },
    '1x1': {
        'form': '0.1*(@0+@1*x)*(1+@2*y)',
        'constraints': _generate_constraints(3)
    },
    '1x2': {
        'form': '0.1*(@0+@1*x)*(1+@2*y+@3*y*y)',
        'constraints': _generate_constraints(4)
    },
    '2x1': {
        'form': '0.1*(@0+@1*x+@2*x**2)*(1+@3*y)',
        'constraints': _generate_constraints(4)
    },
    '2x2': {
        'form': '0.1*(@0+@1*x+@2*x**2)*(1+@3*y+@4*y**2)',
        'constraints': _generate_constraints(5)
    },
    '2x3': {
        'form': '0.1*(@0+@1*x+@2*x*x)*(1+@3*y+@4*y*y+@5*y*y*y)',
        'constraints': _generate_constraints(6)
    },
    '3x2': {
        'form': '0.1*(@0+@1*x+@2*x*x+@3*x*x*x)*(1+@4*y+@5*y*y)',
        'constraints': _generate_constraints(6)
    }
}

def test_make(workspace='',fr={}):
    
    twoD = TwoDAlphabet('{}fits'.format(workspace), 'XHYbbWW.json', findreplace=fr, loadPrevious=False)

    '''
    qcd_hists = twoD.InitQCDHists()

    binning, _ = twoD.GetBinningFor('SR_fail')

    # Set up QCD estimate in SR_fail
    fail_name = 'Background_SR_fail'
    qcd_f = BinnedDistribution(fail_name, qcd_hists['SR_fail'], binning, constant=False)
    twoD.AddAlphaObj('Background_SR_fail', 'SR_fail', qcd_f, title='QCD')

    # set up QCD estimate in ttbarCR_fail
    ttfail_name = 'Background_ttbarCR_fail'
    qcd_ftt = BinnedDistribution(ttfail_name, qcd_hists['ttbarCR_fail'], binning, constant=False)
    twoD.AddAlphaObj('Background_ttbarCR_fail','ttbarCR_fail', qcd_ftt, title='QCD')

    # Try all TFs for the SR and ttbarCR
    for opt_name, opt in _rpf_options.items():
        # TF for SR_fail -> SR_pass
        qcd_rpf_SR = ParametricFunction(
            'Background_SR_rpf_%s'%opt_name, binning, opt['form'],
            constraints = opt['constraints']
        )
        # TF for ttbarCR_fail -> ttbarCR_pass
        qcd_rpf_ttbarCR = ParametricFunction(
            'Background_ttbarCR_rpf_%s'%opt_name, binning, opt['form'],
            constraints = opt['constraints']
        )

        # QCD estimate in SR pass
        qcd_p = qcd_f.Multiply(fail_name.replace('fail','pass')+'_'+opt_name, qcd_rpf_SR)
        twoD.AddAlphaObj('Background_SR_pass_%s'%opt_name, 'SR_pass', qcd_p, title='QCD')
        # QCD estimate in ttbarCR pass
        qcd_ptt = qcd_ftt.Multiply(ttfail_name.replace('fail','pass')+'_'+opt_name, qcd_rpf_ttbarCR)
        twoD.AddAlphaObj('Background_ttbarCR_pass_%s'%opt_name, 'ttbarCR_pass', qcd_ptt, title='QCD')
    '''

    twoD.Save()

def test_fit(workspace='', signal='', SRtf='', CRtf='', defMinStrat=0, extra='--robustHesse 1', rMin=-1, rMax=10, verbosity=2):

    working_area = '{}fits'.format(workspace)
    twoD = TwoDAlphabet(working_area, '{}/runConfig.json'.format(working_area), loadPrevious=True)

    # create ledger, make an area for it with card
    #subset = twoD.ledger.select(_select_signal, 'XHY-{}'.format(signal), SRtf, CRtf)
    subset = twoD.ledger
    if SRtf == '' and CRtf == '':
        area = 'XHY-{}_area'.format(signal)
    else:
        area = 'XHY-{}-SR{}-CR{}_area'.format(signal,SRtf,CRtf)
    twoD.MakeCard(subset, area)
    # perform fit
    twoD.MLfit(area,rMin=rMin,rMax=rMax,verbosity=verbosity,defMinStrat=defMinStrat,extra=extra)

def test_plot(workspace='', signal='', SRtf='', CRtf=''):
    working_area = '{}fits'.format(workspace)
    twoD = TwoDAlphabet(working_area, '{}/runConfig.json'.format(working_area), loadPrevious=True)
    #subset = twoD.ledger.select(_select_signal, 'XHY-{}'.format(signal), SRtf, CRtf)
    subset = twoD.ledger
    # customize the plots to include region definitions
    subtitles = {
        "pass_ttCR": r"$ParticleNetMD_{HvsQCD}$ Loose;$ParticleNetMD_{WvsQCD}$ Pass",
        "pass_SR": r"$ParticleNetMD_{HvsQCD}$ Pass;$ParticleNetMD_{WvsQCD}$ Pass",
    }

    if SRtf == '' and CRtf == '':
        area = 'XHY-{}_area'.format(signal)
    else:
        area = 'XHY-{}-SR{}-CR{}_area'.format(signal,SRtf,CRtf)

    twoD.StdPlots(area, subset, subtitles=subtitles, prefit=False)
    twoD.StdPlots(area, subset, subtitles=subtitles, prefit=True)

def _gof_for_FTest(twoD, subtag, card_or_w='card.txt'):

    run_dir = twoD.tag+'/'+subtag
    
    with cd(run_dir):
        gof_data_cmd = [
            'combine -M GxxoodnessOfFit',
            '-d '+card_or_w,
            '--algo=saturated',
            '-n _gof_data'
        ]

        gof_data_cmd = ' '.join(gof_data_cmd)
        execute_cmd(gof_data_cmd)

def test_FTest(poly1, poly2, SRorCR='ttCR', signal='2000-1000'):
    '''
    Perform an F-test using existing working areas
    '''
    working_area = 'XHYfits_{}'.format(SRorCR)
    
    twoD = TwoDAlphabet(working_area, '{}/runConfig.json'.format(working_area), loadPrevious=True)
    binning = twoD.binnings['default']
    nBins = (len(binning.xbinList)-1)*(len(binning.ybinList)-1)
    
    # Get number of RPF params and run GoF for poly1
    params1 = twoD.ledger.select(_select_signal, 'XHY-{}'.format(signal), poly1).alphaParams
    rpfSet1 = params1[params1["name"].str.contains("rpf")]
    nRpfs1  = len(rpfSet1.index)
    _gof_for_FTest(twoD, 'XHY-{}-{}_area'.format(signal,poly1), card_or_w='card.txt')
    gofFile1 = working_area+'/XHY-{}-{}_area/higgsCombine_gof_data.GoodnessOfFit.mH120.root'.format(signal,poly1)

    # Get number of RPF params and run GoF for poly2
    params2 = twoD.ledger.select(_select_signal, 'XHY-{}'.format(signal), poly2).alphaParams
    rpfSet2 = params2[params2["name"].str.contains("rpf")]
    nRpfs2  = len(rpfSet2.index)
    _gof_for_FTest(twoD, 'XHY-{}-{}_area'.format(signal,poly2), card_or_w='card.txt')
    gofFile2 = working_area+'/XHY-{}-{}_area/higgsCombine_gof_data.GoodnessOfFit.mH120.root'.format(signal,poly2)

    base_fstat = FstatCalc(gofFile1,gofFile2,nRpfs1,nRpfs2,nBins)
    print(base_fstat)

    def plot_FTest(base_fstat,nRpfs1,nRpfs2,nBins):
        from ROOT import TF1, TH1F, TLegend, TPaveText, TLatex, TArrow, TCanvas, kBlue, gStyle
        gStyle.SetOptStat(0000)

        if len(base_fstat) == 0: base_fstat = [0.0]

        ftest_p1    = min(nRpfs1,nRpfs2)
        ftest_p2    = max(nRpfs1,nRpfs2)
        ftest_nbins = nBins
        fdist       = TF1("fDist", "[0]*TMath::FDist(x, [1], [2])", 0,max(10,1.3*base_fstat[0]))
        fdist.SetParameter(0,1)
        fdist.SetParameter(1,ftest_p2-ftest_p1)
        fdist.SetParameter(2,ftest_nbins-ftest_p2)

        pval = fdist.Integral(0.0,base_fstat[0])
        print('P-value: %s'%pval)

        c = TCanvas('c','c',800,600)    
        c.SetLeftMargin(0.12) 
        c.SetBottomMargin(0.12)
        c.SetRightMargin(0.1)
        c.SetTopMargin(0.1)
        ftestHist_nbins = 30
        ftestHist = TH1F("Fhist","",ftestHist_nbins,0,max(10,1.3*base_fstat[0]))
        ftestHist.GetXaxis().SetTitle("F = #frac{-2log(#lambda_{1}/#lambda_{2})/(p_{2}-p_{1})}{-2log#lambda_{2}/(n-p_{2})}")
        ftestHist.GetXaxis().SetTitleSize(0.025)
        ftestHist.GetXaxis().SetTitleOffset(2)
        ftestHist.GetYaxis().SetTitleOffset(0.85)
        
        ftestHist.Draw("pez")
        ftestobs  = TArrow(base_fstat[0],0.25,base_fstat[0],0)
        ftestobs.SetLineColor(kBlue+1)
        ftestobs.SetLineWidth(2)
        fdist.Draw('same')

        ftestobs.Draw()
        tLeg = TLegend(0.6,0.73,0.89,0.89)
        tLeg.SetLineWidth(0)
        tLeg.SetFillStyle(0)
        tLeg.SetTextFont(42)
        tLeg.SetTextSize(0.03)
        tLeg.AddEntry(ftestobs,"observed = %.3f"%base_fstat[0],"l")
        tLeg.AddEntry(fdist,"F-dist, ndf = (%.0f, %.0f) "%(fdist.GetParameter(1),fdist.GetParameter(2)),"l")
        tLeg.Draw("same")

        model_info = TPaveText(0.2,0.6,0.4,0.8,"brNDC")
        model_info.AddText('p1 = '+poly1)
        model_info.AddText('p2 = '+poly2)
        model_info.AddText("p-value = %.2f"%(1-pval))
        model_info.Draw('same')
        
        latex = TLatex()
        latex.SetTextAlign(11)
        latex.SetTextSize(0.06)
        latex.SetTextFont(62)
        latex.SetNDC()
        latex.DrawLatex(0.12,0.91,"CMS")
        latex.SetTextSize(0.05)
        latex.SetTextFont(52)
        latex.DrawLatex(0.65,0.91,"Preliminary")
        latex.SetTextFont(42)
        latex.SetTextFont(52)
        latex.SetTextSize(0.045)
        c.SaveAs(working_area+'/ftest_{0}_vs_{1}_notoys.png'.format(poly1,poly2))

    plot_FTest(base_fstat,nRpfs1,nRpfs2,nBins)

def test_GoF(workspace, signal, SRtf='', CRtf='', condor=False, extra='', appendName=''):
    working_area = '{}fits'.format(workspace)
    twoD = TwoDAlphabet(working_area, '{}/runConfig.json'.format(working_area), loadPrevious=True)
    signame = 'XHY-'+signal

    if SRtf == '' and CRtf == '':
        area = 'XHY-{}_area'.format(signal)
    else:
        area = 'XHY-{}-SR{}-CR{}_area'.format(signal,SRtf,CRtf)

    if not os.path.exists(twoD.tag+'/'+area+'/card.txt'):
        print('{}/{}-area/card.txt does not exist, making card'.format(twoD.tag,signame))
        subset = twoD.ledger
        #subset = twoD.ledger.select(_select_signal, signame, SRtf, CRtf)
        twoD.MakeCard(subset, area)
    if condor == False:
        twoD.GoodnessOfFit(
            area, ntoys=500, freezeSignal=0,
            condor=False, card_or_w='initialFitWorkspace.root', extra=extra, 
            makeEnv=True
        )
    else:
        twoD.GoodnessOfFit(
            area, ntoys=500, freezeSignal=0,
            condor=True, njobs=50, card_or_w='initialFitWorkspace.root', 
            extra=extra
        )

def test_GoF_plot(workspace, signal, SRtf='', CRtf='', condor=False, appendName = ''):
    '''Plot the GoF in XHYfits_<SRorCR>/XHY-<signal>_area (condor=True indicates that condor jobs need to be unpacked)'''
    signame = 'XHY-'+signal

    if SRtf == '' and CRtf == '':
        area = 'XHY-{}_area'.format(signal)
    else:
        area = 'XHY-{}-SR{}-CR{}_area'.format(signal,SRtf,CRtf)
    
    plot.plot_gof(f'{workspace}fits',area, condor=condor)

def test_limits(workspace, signal, SRtf, CRtf):
    working_area = '{}fits'.format(workspace)

    if SRtf == '' and CRtf == '':
        area = 'XHY-{}_area'.format(signal)
    else:
        area = 'XHY-{}-SR{}-CR{}_area'.format(signal,SRtf,CRtf)

    twoD = TwoDAlphabet(working_area, '{}/runConfig.json'.format(working_area), loadPrevious=True)
    twoD.Limit(
        subtag=area,
        blindData=False,        # BE SURE TO CHANGE THIS IF YOU NEED TO BLIND YOUR DATA
        verbosity=2,
        card_or_w='initialFitWorkspace.root',
        condor=False
    )


def test_Impacts(workspace, signal='1000-500', SRtf='', CRtf=''):
    working_area = '{}fits'.format(workspace)
    twoD = TwoDAlphabet(working_area, '{}/runConfig.json'.format(working_area), loadPrevious=True)
    twoD.Impacts('XHY-{}_area'.format(signal), rMin=-1, rMax=4, extra='')


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-w', type=str, dest='workspace',
                        action='store', default='jointSRttCR',
                        help='workspace name')
    parser.add_argument('-s', type=str, dest='sigmass',
                        action='store', default='1000-500',
                        help='mass of X and Y candidates')
    parser.add_argument('--condor', dest='condor',
                        action='store_true',
                        help='If passed as argument, use Condor for methods')
    parser.add_argument('--make', dest='make',
                        action='store_true', 
                        help='If passed as argument, create 2DAlphabet workspace')
    parser.add_argument('--SRtf', type=str, dest='SRtf',
                        action='store', default='', required=False,
                        help='TF parameterization for SR tf')
    parser.add_argument('--CRtf', type=str, dest='CRtf',
                        action='store', default='', required=False,
                        help='TF parameterization for CR tf')
    parser.add_argument('--fit', dest='fit',
                        action='store_true',
                        help='If passed as argument, run the NLL fit')
    parser.add_argument('--plot', dest='plot',
                        action='store_true',
                        help='If passed as argument, plot the result of the fit')
    parser.add_argument('--gof', dest='gof',
                        action='store_true',
                        help='If passed as argument, run GoF test for the fit')
    parser.add_argument('--rinj', type=float, dest='rinj',
                        action='store', default='0.0',
                        help='Value of signal strength to inject')
    parser.add_argument('--inject', dest='inject',
                        action='store_true',
                        help='If passed as argument, run signal injection test for the fit')
    parser.add_argument('--impacts', dest='impacts',
                        action='store_true',
                        help='If passed as argument, run impacts for the fit')
    parser.add_argument('--limit', dest='limit',
                        action='store_true',
                        help='If passed as argument, run the limit for the fit')
    parser.add_argument('--analyzeNLL', dest='analyzeNLL',
                        action='store_true',
                        help='Analyze NLL as function of all nuisances')

    # Fit options
    parser.add_argument('--strat', dest='strat',
                        action='store', default='0',
                        help='Default minimizer strategy')
    parser.add_argument('--tol', dest='tol',
                        action='store', default='0.1',
                        help='Default minimizer tolerance')
    parser.add_argument('--robustFit', dest='robustFit',
                        action='store_true',
                        help='If passed as argument, uses robustFit algo')
    parser.add_argument('--robustHesse', dest='robustHesse',
                        action='store_true',
                        help='If passed as argument, uses robustHesse algo')
    parser.add_argument('--rMin', dest='rMin',
                        action='store', default='-1',
                        help='Minimum allowed signal strength')
    parser.add_argument('--rMax', dest='rMax',
                        action='store', default='10',
                        help='Maximium allowed signal strength')
    parser.add_argument('-v', dest='verbosity',
                        action='store', default='2',
                        help='Combine verbosity')

    args = parser.parse_args()

    if args.make:
        mX   = args.sigmass.split('-')[0]
        mY = args.sigmass.split('-')[-1]
        fr = {'XHY-MX-MY':f'XHY-{mX}-{mY}'}
        test_make(args.workspace, fr=fr)
    if args.fit:
        if (args.robustFit) and (args.robustHesse):
            raise ValueError('Cannot use both robustFit and robustHesse algorithms simultaneously') 
        elif (args.robustFit) or (args.robustHesse):
            if args.robustFit:
                algo = f'--robustFit 1'
            else:
                algo = f'--robustHesse 1'
        else:
            algo = ''
        test_fit(
            args.workspace, 
            args.sigmass, 
            SRtf=args.SRtf,
            CRtf=args.CRtf,
            defMinStrat=int(args.strat), 
            extra=f'{algo} --cminDefaultMinimizerTolerance {args.tol}',
            rMin=args.rMin,
            rMax=args.rMax,
            verbosity=args.verbosity
        )
    if args.plot:
        test_plot(args.workspace, args.sigmass, SRtf=args.SRtf, CRtf=args.CRtf)
    if args.gof:
        test_GoF(args.workspace, args.sigmass, SRtf=args.SRtf, CRtf=args.CRtf, condor=args.condor, extra='--fixedSignalStrength 0')
        test_GoF_plot(args.workspace, args.sigmass, SRtf=args.SRtf, CRtf=args.CRtf, condor=args.condor)
    if args.limit:
        test_limits(args.workspace, args.sigmass, args.SRtf, args.CRtf)
    # ignore the rest of this stuff for now
    if args.inject:
        #test_SigInj(args.workspace, args.rinj, args.sigmass, args.SRtf, args.CRtf, condor=args.condor)
        test_SigInj_plot(args.workspace, args.rinj, args.sigmass, args.SRtf, args.CRtf, condor=args.condor)
    if args.impacts:
        test_Impacts(args.workspace, args.sigmass, args.SRtf, args.CRtf)
    if args.analyzeNLL:
        test_analyze(args.workspace, args.sigmass, args.SRtf, args.CRtf)

