
from python.alcaval_steps import *
workflows = Matrix()

# CRUZET 2021
workflows[1.1] = ['CRUZET2022', ['Cosmics2021', 'HLT_CRUZET2021', 'RECO_CRUZET2021', 'HARVEST_CRUZET2021']]
workflows[1.2] = ['CRUZET2022', ['Cosmics2021', 'RECO_CRUZET2021', 'HARVEST_CRUZET2021']]
workflows[1.3] = ['CRUZET2022', ['ExpressCosmics2021', 'HLT_CRUZET2021', 'RECO_CRUZET2021', 'HARVEST_CRUZET2021']]
workflows[1.4] = ['CRUZET2022', ['ExpressCosmics2021', 'RECO_CRUZET2021', 'HARVEST_CRUZET2021']]

# PBT 2021
workflows[2.1] = ['PBT2021', ['MinimumBias2021', 'HLT_PBT2021', 'RECO_PBT2021', 'HARVESTD']]
workflows[2.2] = ['PBT2021', ['MinimumBias2021', 'RECOPE_PBT21', 'HARVESTD']]
workflows[2.3] = ['PBT2021', ['ZeroBias2021', 'HLT_PBT2021', 'RECO_PBT2021', 'HARVESTD']]
workflows[2.4] = ['PBT2021', ['ZeroBias2021', 'RECOPE_PBT21', 'HARVESTD']]
workflows[2.5] = ['PBT2021', ['HLTPhysics2021', 'HLT_PBT2021', 'RECO_PBT2021', 'HARVESTD']]
workflows[2.6] = ['PBT2021', ['HLTPhysics2021', 'RECOPE_PBT21', 'HARVESTD']]

# MWGR 2022
workflows[3.1] = ['MWGR2022', ['HcalNZS2022', 'HLT_MWGR2022', 'RECO_MWGR2022', 'HARVEST_MWGR2022']]
workflows[3.2] = ['MWGR2022', ['HcalNZS2022', 'RECO_MWGR2022', 'HARVEST_MWGR2022']]

# CRAFT 2022
workflows[4.1] = ['CRAFT2022', ['HLTPhysics2022', 'HLT_CRAFT22', 'RECO_CRAFT2022', 'HARVEST_CRAFT22']]
workflows[4.2] = ['CRAFT2022', ['HLTPhysics2022', 'RECO_CRAFT2022', 'HARVEST_CRAFT22']]
