import os, ROOT, subprocess
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import matplotlib.ticker as mticker
from scipy import interpolate
import matplotlib

plt.style.use(hep.style.CMS)
hep.style.use("CMS")
formatter = mticker.ScalarFormatter(useMathText=True)
formatter.set_powerlimits((-3, 3))
plt.rcParams.update({"font.size": 20})

# 0-4 are m2,m1,exp,p1,p2 sigma limits, 5 is observed
limits = {0: [], 1: [], 2: [], 3: [], 4: []}
failed = {0: [], 1: [], 2: [], 3: [], 4: []}

base_str = '{MX}-{MY}_fits/XHY-{MX}-{MY}_area/higgsCombineTest.AsymptoticLimits.mH120.root'

samples = open('valid_signals.txt','r').readlines()
for sample in samples:
    signal = sample.strip('\n')
    MX = signal.split('-')[0]
    MY = signal.split('-')[-1]
    filename = base_str.format(MX=MX,MY=MY)

    if not os.path.exists(filename):
        print(f'Limits do not exist for signal {MX}-{MY}')
        for i in range(5):
            failed[i].append([int(MX), int(MY), u'$\u274c$']) 
        continue
    else:
        f = ROOT.TFile.Open(filename,'READ')
        limitTree = f.Get('limit')
        print(signal)
        if int(MX) < 1000: xsec = 0.1
        elif int(MX) < 2000: xsec = 0.01
        else: xsec = 0.001
        for i in range(5): # skip observed for now
            limitTree.GetEntry(i)
            limit = limitTree.limit * xsec * 1000 #fb
            limits[i].append([int(MX), int(MY), limit])

for key in limits:
    limits[key] = np.array(limits[key])
    failed[key] = np.array(failed[key])

def scatter2d(arr, failarr, title, name):
    plt.style.use(hep.style.CMS)
    fig, ax = plt.subplots(figsize=(14, 12))
    #fig = plt.figure(figsize=(14, 12))
    #ax = fig.add_subplot(111)
    '''
    print(failarr)
    ax.scatter(
        failarr[:, 0],
        failarr[:, 1],
        s=150,
        marker='o'
    )
    '''
    mappable = plt.scatter(
        arr[:, 0],
        arr[:, 1],
        s=150,
        c=arr[:, 2],
        cmap="turbo",
        norm=matplotlib.colors.LogNorm(vmin=0.01, vmax=100),
    )
    plt.title(title)
    plt.xlabel(r"$m_{X}$ [GeV]")
    plt.ylabel(r"$m_{Y}$ [GeV]")
    plt.colorbar(mappable)

    plt.savefig(name, bbox_inches="tight")

# Y masses
mys  = np.logspace(np.log10(60), np.log10(2800), 100, base=10)
# X masses
mxs = np.logspace(np.log10(240), np.log10(4000), 100, base=10)

# not sure why - just reverse X and Y here
xx, yy = np.meshgrid(mys, mxs)

interpolated = {}
grids = {}


for key, val in limits.items():
    interpolated[key] = interpolate.LinearNDInterpolator(val[:, :2], np.log(val[:, 2]))
    grids[key] = np.exp(interpolated[key](xx, yy))


for key in range(5):
    if key == 0: label = '2.5'
    elif key == 1: label = '16'
    elif key == 2: label = '50'
    elif key == 3: label = '84'
    elif key == 4: label = '97.5'
    val = limits[key]
    scatter2d(val, failed[key], "Expected {}% Limit [fb]".format(label), "limit2D_scatter_{}.png".format(label))
