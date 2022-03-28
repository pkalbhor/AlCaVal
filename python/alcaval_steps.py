from __future__ import absolute_import
from .core import *

steps = Steps()
steps['MinimumBias2021']={'INPUT':InputInfo(dataSet='/MinimumBias/Commissioning2021-v1/RAW',ls={346512: [[1,400]]})}
steps['ZeroBias2021']={'INPUT':InputInfo(dataSet='/ZeroBias/Commissioning2021-v1/RAW', ls={346512: [[1,400]]})}
steps['HLTPhysics2021']={'INPUT':InputInfo(dataSet='/HLTPhysics/Commissioning2021-v1/RAW',ls={346512: [[1,400]]})}

# step1 HLT: for run3
step2Defaults = {'--process':'reHLT',
                      '-s':'L1REPACK,HLT',
                      '--conditions':'auto:run3_data',
                      '--data':'',
                      '--eventcontent': 'FEVTDEBUGHLT',
                      '--datatier': 'FEVTDEBUGHLT',
                      }

hltKeyDefault='GRun'
steps['HLTDR2_2017'] = merge( [ {'-s':'L1REPACK,HLT:%s'%hltKeyDefault,},{'--era' : 'Run3'}, step2Defaults ] )

# step3
step3Defaults = {
                  '-s'            : 'RAW2DIGI,L1Reco,RECO,EI,PAT,DQM:DQMOffline+offlineValidationHLTSource',
                  '--conditions'  : 'auto:run3_data',
                  '--no_exec'     : '',
                  '--data'        : '',
                  '--datatier'    : 'RECO,DQMIO',
                  '--eventcontent': 'RECO,DQM',
                  }

steps['RECODR2_2017']=merge([{'--scenario':'pp','--era':'Run3','--customise':'Configuration/DataProcessing/RecoTLR.customisePostEra_Run3,RecoLocalCalo/Configuration/customiseHBHEreco.hbheUseM0FullRangePhase1'},step3Defaults])

#data
steps['HARVESTD']={'-s':'HARVESTING',
                   '--conditions':'auto:run3_data',
                   '--data':'',
                   '--filetype':'DQM',
                   '--scenario':'pp'}

steps['HARVEST2017ZB'] = merge([ {'--era':'Run3','-s':' HARVESTING:@rerecoZeroBiasFakeHLT+@miniAODDQM'}, steps['HARVESTD'] ])
