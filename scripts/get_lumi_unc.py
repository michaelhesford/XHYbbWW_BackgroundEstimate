import numpy as np 

LUMI = {  # in pb^-1
    "2016": 16810.0,
    "2016APV": 19500.0,
    "2017": 41480.0,
    "2018": 59830.0,
}

full_lumi = np.sum(list(LUMI.values()))
lumi_1718 = LUMI['2017'] + LUMI['2018']

base_str = '''
        "lumi_%s": {
            "CODE": 0,
            "VAL": %s
        },
'''

for syst in ['16','17','18','1718','correlated']:
    if syst == '16':
        val = 1.01 
    elif syst == '17':
        val = 1.02 
    elif syst == '18':
        val = 1.015 
    elif syst == '1718':
        val = (1.006 ** (LUMI["2017"] / lumi_1718)) * (1.002 ** (LUMI["2018"] / lumi_1718))
    elif syst == 'correlated':
        val = (1.006 ** ((LUMI["2016"] + LUMI["2016APV"]) / full_lumi)) * (1.009 ** (LUMI["2017"] / full_lumi)) * (1.02 ** (LUMI["2018"] / full_lumi))
    val = round(val,4)
    print(base_str%(syst,val))
