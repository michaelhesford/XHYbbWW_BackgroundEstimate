import matplotlib
matplotlib.use('Agg')

import ROOT as r
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mplhep as hep
import ctypes
from pathlib import Path

matplotlib.use('Agg')
r.gROOT.SetBatch(True)
r.gStyle.SetOptFit(111)

def plot_limits(MX_values, output_name, prefit_xsec_in_fb={}, theory=[], observed=False):
    limits = {
        "expected": [],
        "observed": [],
        "minus_2sigma": [],
        "minus_1sigma": [],
        "plus_1sigma": [],
        "plus_2sigma": []
    }

    path_template = '{MX}-125_fits/XHY-{MX}-125_area/higgsCombineTest.AsymptoticLimits.mH120.root'
    for MX in MX_values:
        path = path_template.format(MX=MX)
        rdf = r.RDataFrame('limit',path)
        data = rdf.AsNumpy()

        limits["expected"].append(data['limit'][2]*prefit_xsec_in_fb[MX])
        limits["minus_2sigma"].append(data['limit'][0]*prefit_xsec_in_fb[MX])
        limits["minus_1sigma"].append(data['limit'][1]*prefit_xsec_in_fb[MX])
        limits["plus_1sigma"].append(data['limit'][3]*prefit_xsec_in_fb[MX])
        limits["plus_2sigma"].append(data['limit'][4]*prefit_xsec_in_fb[MX])
        if observed:
            limits["observed"].append(data['limit'][5]*prefit_xsec_in_fb[MX]) #Don't have observed yet

    for key in limits:
        limits[key] = np.array(limits[key])

    plt.style.use([hep.style.CMS])
    f, ax = plt.subplots()

    hep.cms.text("WiP",loc=0)
    lumiText = "138 $fb^{-1} (13 TeV)$"    
    hep.cms.lumitext(lumiText)
    ax.set_xlim(MX_values[0], MX_values[-1])

    green = '#607641' 
    yellow = '#F5BB54' 

    plt.fill_between(MX_values, limits["minus_2sigma"], limits["plus_2sigma"], color=yellow, label='95% expected')
    plt.fill_between(MX_values, limits["minus_1sigma"], limits["plus_1sigma"], color=green, label='68% expected')
    plt.plot(MX_values, limits["expected"], color='black', linestyle='--', label='Median expected')
    if observed:
        plt.plot(MX_values, limits["observed"], color='red', marker='o', linestyle='-', label='Observed 95% CL upper limit')

    if theory:
        from scipy.interpolate import make_interp_spline, BSpline
        xnew = np.linspace(MX_values[0],MX_values[-1],300)
        spl = make_interp_spline(MX_values, theory, k=3)
        theory_smooth = spl(xnew)
        plt.plot(xnew, theory_smooth, label=r'$\sigma$ theory')

    plt.ylabel(r'$\sigma B(X\to HY) [fb]$',horizontalalignment='right', y=1.0)
    plt.xlabel("$m_{X}$ [GeV]", horizontalalignment='right', x=1.0)
    plt.text(2200, 40, r'$m_{Y} = 125$ GeV')
    plt.yscale('log')
    plt.ylim(0.1, 10**3)
    plt.legend(loc=(0.10,0.60)
      , title='95% CL upper limits'
      ,ncol=2
      ,title_fontsize=17
      ,fontsize=17
      )

    plt.legend()

    print(f"Saving {output_name}.png")
    plt.savefig(f"{output_name}.pdf")
    plt.savefig(f"{output_name}.png")

MX_values = [280,300,320,360,400,500,600,700,800,900,1000,1400,1600,1800,2000,2200,2400,2500,2600,2800,3000,3500,4000] #1200
xsec_pb = {
    280:0.1,
    300:0.1,
    320:0.1,
    360:0.1,
    400:0.1,
    500:0.1,
    600:0.1,
    700:0.1,
    800:0.1,
    900:0.1,
    1000:0.01,
    1200:0.01,
    1400:0.01,
    1600:0.01,
    1800:0.01,
    2000:0.001,
    2200:0.001,
    2400:0.001,
    2500:0.001,
    2600:0.001,
    2800:0.001,
    3000:0.001,
    3500:0.001,
    4000:0.001
}
xsec_fb = {k:v*1000 for k,v in xsec_pb.items()}

theory_fb = [
    45.92,
    25.327,
    14.550,
    3.390,
    2.197,
    1.448,
    0.9743,
    0.4588,
    0.3201,
    0.0671,
    0.0600,
    0.0600,
    0.0600
]

plot_limits(MX_values, "xhy_limits_MY_125", observed=False, prefit_xsec_in_fb=xsec_fb,theory=[])
