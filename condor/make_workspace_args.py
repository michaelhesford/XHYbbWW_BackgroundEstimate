import glob

# Use snapshots, since this will only get signal files that have been successfully processed
inDir = '/uscms/home/mhesford/nobackup/XHYbbWW/CMSSW_12_3_5/src/semileptonic/snapshots/XHY*.txt'
snapshotFiles = glob.glob(inDir)
signalFiles = [i.split('/')[-1].split('.')[0].split('_')[0] for i in snapshotFiles if ('_18' in i)]
sout = open('condor/XHY_signals.txt','w')
for sig in signalFiles:
    sout.write(sig+'\n')
sout.close()

f = open('condor/XHY_signals.txt','r')
signames = [i.strip() for i in f.readlines()]
f.close()

'''
signames = [
'XHY-3000-2000',
'XHY-3500-1400',
'XHY-1000-150',
'XHY-1400-400',
'XHY-1600-600',
'XHY-1800-90',
'XHY-240-80',
'XHY-2400-1100',
'XHY-2400-250',
'XHY-2400-400',
'XHY-2400-500',
'XHY-3000-1200',
'XHY-3500-2200',
'XHY-500-90',
'XHY-600-400',
'XHY-900-60',
'XHY-2600-400',
'XHY-2800-500',
'XHY-4000-1100',
'XHY-800-250',
'XHY-800-300',
'XHY-3000-2800'
]
'''
out = open('condor/workspace_args_xhy.txt','w')
for sig in signames:
    MX   = sig.split('-')[1]
    MY = sig.split('-')[2]

    out.write(f'-w {MX}-{MY}_ -s {MX}-{MY} --make --fit --limit\n')
