import os
from python.StepsReader import StepsReader
from python.MatrixRunner import MatrixRunner
from python.MatrixInjector import MatrixInjector, performInjectionOptionTest

import argparse
usage = 'usage: runAlCaMatrix.py --show -s '
parser = argparse.ArgumentParser(usage,formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-b','--batchName',
        help='relval batch: suffix to be appended to Campaign name',
        dest='batchName',
        default='')
parser.add_argument('-m','--memoryOffset',
        help='memory of the wf for single core',
        dest='memoryOffset',
        type=int,
        default=3000)
parser.add_argument('--addMemPerCore',
        help='increase of memory per each n > 1 core:  memory(n_core) = memoryOffset + (n_core-1) * memPerCore',
        dest='memPerCore',
        type=int,
        default=1500)
parser.add_argument('-j','--nproc',
        help='number of processes. 0 Will use 4 processes, not execute anything but create the wfs',
        dest='nProcs',
        type=int,
        default=4)
parser.add_argument('-t','--nThreads',
        help='number of threads per process to use in cmsRun.',
        dest='nThreads',
        type=int,
        default=8)
parser.add_argument('--nStreams',
        help='number of streams to use in cmsRun.',
        dest='nStreams',
        type=int,
        default=2)
parser.add_argument('--numberEventsInLuminosityBlock',
        help='number of events in a luminosity block',
        dest='numberEventsInLuminosityBlock',
        type=int,
        default=-1)
parser.add_argument('-n','--showMatrix',
        help='Only show the worflows. Use --ext to show more',
        dest='show',
        default=False,
        action='store_true')
parser.add_argument('-e','--extended',
        help='Show details of workflows, used with --show',
        dest='extended',
        default=False,
        action='store_true')
parser.add_argument('-s','--selected',
        help='Run a pre-defined selected matrix of wf. Deprecated, please use -l limited',
        dest='restricted',
        default=False,
        action='store_true')
parser.add_argument('-l','--list',
        help='Comma separated list of workflow to be shown or ran.',
        dest='testList',
        default=None)
parser.add_argument('-r','--raw',
        help='Temporary dump the .txt needed for prodAgent interface. To be discontinued soon. Argument must be the name of the set (standard, pileup,...)',
        dest='raw')
parser.add_argument('-i','--useInput',
        help='Use recyling where available. Either all, or a comma separated list of wf number.',
        dest='useInput',
        type=lambda x: x.split(','),
        default=None)
parser.add_argument('-w','--what',
        help='Specify the set to be used. Argument must be the name of a set (standard, pileup,...) or multiple sets separated by commas (--what standard,pileup )',
        dest='what',
        default='all')
parser.add_argument('--step1',
        help='Used with --raw. Limit the production to step1',
        dest='step1Only',
        default=False)
parser.add_argument('--maxSteps',
        help='Only run maximum on maxSteps. Used when we are only interested in first n steps.',
        dest='maxSteps',
        default=9999,
        type=int)
parser.add_argument('--fromScratch',
        help='Comma separated list of wf to be run without recycling. all is not supported as default.',
        dest='fromScratch',
        type=lambda x: x.split(','),
        default=None)
parser.add_argument('--refRelease',
        help='Allow to modify the recycling dataset version',
        dest='refRel',
        default=None)
parser.add_argument('--wmcontrol',
        help='Create the workflows for injection to WMAgent. In the WORKING. -wmcontrol init will create the the workflows, -wmcontrol test will dryRun a test, -wmcontrol submit will submit to wmagent',
        choices=['init','test','submit','force'],
        dest='wmcontrol',
        default=None)
parser.add_argument('--revertDqmio',
        help='When submitting workflows to wmcontrol, force DQM outout to use pool and not DQMIO',
        choices=['yes','no'],
        dest='revertDqmio',
        default='no')
parser.add_argument('--optionswm',
        help='Specify a few things for wm injection',
        default='',
        dest='wmoptions')
parser.add_argument('--keep',
        help='allow to specify for which comma separated steps the output is needed',
        default=None)
parser.add_argument('--label',
        help='allow to give a special label to the output dataset name',
        default='')
parser.add_argument('--command',
        help='provide a way to add additional command to all of the cmsDriver commands in the matrix',
        dest='command',
        action='append',
        default=None)
parser.add_argument('--apply',
        help='allow to use the --command only for 1 comma separeated',
        dest='apply',
        default=None)
parser.add_argument('--workflow',
        help='define a workflow to be created or altered from the matrix',
        action='append',
        dest='workflow',
        default=None)
parser.add_argument('--dryRun',
        help='do not run the wf at all',
        action='store_true',
        dest='dryRun',
        default=False)
parser.add_argument('--testbed',
        help='workflow injection to cmswebtest (you need dedicated rqmgr account)',
        dest='testbed',
        default=False,
        action='store_true')
parser.add_argument('--noCafVeto',
        help='Run from any source, ignoring the CAF label',
        dest='cafVeto',
        default=True,
        action='store_false')
parser.add_argument('--overWrite',
        help='Change the content of a step for another. List of pairs.',
        dest='overWrite',
        default=None)
parser.add_argument('--noRun',
        help='Remove all run list selection from wfs',
        dest='noRun',
        default=False,
        action='store_true')
parser.add_argument('--das-options',
        help='Options to be passed to dasgoclient.',
        dest='dasOptions',
        default="--limit 0",
        action='store')
parser.add_argument('--job-reports',
        help='Dump framework job reports',
        dest='jobReports',
        default=False,
        action='store_true')
parser.add_argument('--ibeos',
        help='Use IB EOS site configuration',
        dest='IBEos',
        default=False,
        action='store_true')
parser.add_argument('--sites',
        help='Run DAS query to get data from a specific site. Set it to empty string to search all sites.',
        dest='dasSites',
        default='T2_CH_CERN',
        action='store')
parser.add_argument('--interactive',
        help="Open the Matrix interactive shell",
        action='store_true',
        default=False)
parser.add_argument('--dbs-url',
        help='Overwrite DbsUrl value in JSON submitted to ReqMgr2',
        dest='dbsUrl',
        default=None,
        action='store')
gpugroup = parser.add_argument_group('GPU-related options','These options are only meaningful when --gpu is used, and is not set to forbidden.')

gpugroup.add_argument('--gpu','--requires-gpu',
      help='Enable GPU workflows. Possible options are "forbidden" (default), "required" (implied if no argument is given), or "optional".',
      dest='gpu',
      choices=['forbidden', 'optional', 'required'],
      nargs='?',
      const='required',
      default='forbidden',
      action='store')
gpugroup.add_argument('--gpu-memory',
      help='Specify the minimum amount of GPU memory required by the job, in MB.',
      dest='GPUMemoryMB',
      type=int,
      default=8000)
gpugroup.add_argument('--cuda-capabilities',
      help='Specify a comma-separated list of CUDA "compute capabilities", or GPU hardware architectures, that the job can use.',
      dest='CUDACapabilities',
      type=lambda x: x.split(','),
      default='6.0,6.1,6.2,7.0,7.2,7.5,8.0,8.6')
# read the CUDA runtime version included in CMSSW
cudart_version = None
libcudart = os.path.realpath(os.path.expandvars('$CMSSW_RELEASE_BASE/external/$SCRAM_ARCH/lib/libcudart.so'))
if os.path.isfile(libcudart):
    cudart_basename = os.path.basename(libcudart)
    cudart_version = '.'.join(cudart_basename.split('.')[2:4])
gpugroup.add_argument('--cuda-runtime',
      help='Specify major and minor version of the CUDA runtime used to build the application.',
      dest='CUDARuntime',
      default=cudart_version)

gpugroup.add_argument('--force-gpu-name',
      help='Request a specific GPU model, e.g. "Tesla T4" or "NVIDIA GeForce RTX 2080". The default behaviour is to accept any supported GPU.',
      dest='GPUName',
      default='')

gpugroup.add_argument('--force-cuda-driver-version',
      help='Request a specific CUDA driver version, e.g. 470.57.02. The default behaviour is to accept any supported CUDA driver version.',
      dest='CUDADriverVersion',
      default='')

gpugroup.add_argument('--force-cuda-runtime-version',
      help='Request a specific CUDA runtime version, e.g. 11.4. The default behaviour is to accept any supported CUDA runtime version.',
      dest='CUDARuntimeVersion',
      default='')

opt = parser.parse_args()
if opt.command: opt.command = ' '.join(opt.command)
os.environ["CMSSW_DAS_QUERY_SITES"]=opt.dasSites
if opt.IBEos:
    from subprocess import getstatusoutput as run_cmd

# ibeos_cache = os.path.join(os.getenv("LOCALRT"), "ibeos_cache.txt")
# if not os.path.exists(ibeos_cache):
#     err, out = run_cmd("curl -L -s -o %s https://raw.githubusercontent.com/cms-sw/cms-sw.github.io/master/das_queries/ibeos.txt" % ibeos_cache)
# if err:
#     run_cmd("rm -f %s" % ibeos_cache)
#     print("Error: Unable to download ibeos cache information")
#     print(out)
#     sys.exit(err)

for cmssw_env in [ "CMSSW_BASE", "CMSSW_RELEASE_BASE" ]:
    cmssw_base = os.getenv(cmssw_env,None)
    if not cmssw_base: continue
    cmssw_base = os.path.join(cmssw_base,"src/Utilities/General/ibeos")
    if os.path.exists(cmssw_base):
        os.environ["PATH"]=cmssw_base+":"+os.getenv("PATH")
        os.environ["CMS_PATH"]="/cvmfs/cms-ib.cern.ch"
        os.environ["CMSSW_USE_IBEOS"]="true"
        print(">> WARNING: You are using SITECONF from /cvmfs/cms-ib.cern.ch")
        break
if opt.restricted:
    print('Deprecated, please use -l limited')
    if opt.testList:  opt.testList+=',limited'
    else:  opt.testList='limited'

def stepOrIndex(s):
    if s.isdigit():
        return int(s)
    else:
        return s
if opt.apply:
    opt.apply=map(stepOrIndex,opt.apply.split(','))
if opt.keep:
    opt.keep=map(stepOrIndex,opt.keep.split(','))

if opt.testList:
    testList=[]
    for entry in opt.testList.split(','):
        if not entry: continue
        mapped=False
        # for k in predefinedSet:
        #     if k.lower().startswith(entry.lower()) or k.lower().endswith(entry.lower()):
        #         testList.extend(predefinedSet[k])
        #         mapped=True
        #         break
        if not mapped:
            try:
                testList.append(float(entry))
            except:
                print(entry,'is not a possible selected entry')
    opt.testList = list(set(testList))

if opt.wmcontrol:
    performInjectionOptionTest(opt)

def runSelected(opt):

    mrd = StepsReader(opt)
    mrd.prepare(opt.useInput)

    # test for wrong input workflows
    # if opt.testList:
    #     definedWf = [dwf.numId for dwf in mrd.workFlows]
    #     definedSet = set(definedWf)
    #     testSet = set(opt.testList)
    #     undefSet = testSet - definedSet
    #     if len(undefSet)>0: raise ValueError('Undefined workflows: '+', '.join(map(str,list(undefSet))))
    #     duplicates = [wf for wf in testSet if definedWf.count(wf)>1 ]
    #     if len(duplicates)>0: raise ValueError('Duplicated workflows: '+', '.join(map(str,list(duplicates))))

    ret = 0
    if opt.show:
        mrd.show(opt.testList, opt.extended)
        if opt.testList : print('testListected items:', opt.testList)
    else:
        mRunnerHi = MatrixRunner(mrd.workFlows, opt.nProcs, opt.nThreads)
        ret = mRunnerHi.runTests(opt)

    if opt.wmcontrol:
        if ret!=0:
            print('Cannot go on with wmagent injection with failing workflows')
        else:
            wfInjector = MatrixInjector(opt,mode=opt.wmcontrol,options=opt.wmoptions)
            ret= wfInjector.prepare(mrd,
                                    mRunnerHi.runDirs)
            if ret==0:
                wfInjector.upload()
                wfInjector.submit()
    return ret

ret = runSelected(opt)