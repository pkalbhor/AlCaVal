import sys, os

from .WorkFlow import WorkFlow
from python.core import InputInfo
class StepsReader(object):
    # def __init__(self, opt):
    #     self.filesDefault = {'alcaval_standard':True }
    #     self.files = ['alcaval_standard']
    #     self.workFlowSteps = {}
    #     self.workFlows = []
    #     self.wm = opt.wmcontrol
    #     self.revertDqmio=opt.revertDqmio
    #     self.alcavalModule = None
    #     self.what = opt.what
    #     self.filesPrefMap = {'alcaval_standard' : 'std-'}
    #     self.nameList  = {}

    def __init__(self, opt):

        self.reset(opt.what)

        self.wm=opt.wmcontrol
        self.revertDqmio=opt.revertDqmio
        self.addCommand=opt.command
        self.apply=opt.apply
        self.commandLineWf=opt.workflow
        self.overWrite=opt.overWrite

        self.noRun = opt.noRun
        return

    def reset(self, what='all'):

        self.what = what

        #a bunch of information, but not yet the WorkFlow object
        self.workFlowSteps = {}
        #the actual WorkFlow objects
        self.workFlows = []
        self.nameList  = {}
        
        self.filesPrefMap = {'alcaval_standard' : 'std-'}

        self.files = ['alcaval_standard']
        self.filesDefault = {'alcaval_standard':True}

        self.alcavalModule = None
        
        return

    def makeCmd(self, step):

        cmd = ''
        cfg = None
        input = None
        for k,v in step.items():
            if 'no_exec' in k : continue  # we want to really run it ...
            if k.lower() == 'cfg':
                cfg = v
                continue # do not append to cmd, return separately
            if k.lower() == 'input':
                input = v 
                continue # do not append to cmd, return separately
            
            #chain the configs
            #if k.lower() == '--python':
            #    v = 'step%d_%s'%(index,v)
            cmd += ' ' + k + ' ' + str(v)
        return cfg, input, cmd

    def collectSteps(self, fileNameIn):
        prefix = self.filesPrefMap[fileNameIn]
        try:
            _tmpMod = __import__( 'python.'+fileNameIn )
            self.alcavalModule = sys.modules['python.'+fileNameIn]
        except Exception as e:
            print("ERROR importing file ", fileNameIn, str(e))
            return
        for num, wfInfo in self.alcavalModule.workflows.items():
            print(num, wfInfo)

            commands=[]
            wfName = wfInfo[0]
            stepList = wfInfo[1]
            # upgrade case: workflow has basic name, key[, suffix (only special workflows)]
            wfKey = ""
            wfSuffix = ""
            if isinstance(wfName, list) and len(wfName)>1:
                if len(wfName)>2: wfSuffix = wfName[2]
                wfKey = wfName[1]
                wfName = wfName[0]
            # if no explicit name given for the workflow, use the name of step1
            if wfName.strip() == '': wfName = stepList[0]
            # option to specialize the wf as the third item in the WF list
            addTo=None
            addCom=None
            if len(wfInfo)>=3:
                addCom=wfInfo[2]
                if not isinstance(addCom, list):   addCom=[addCom]
                #print 'added dict',addCom
                if len(wfInfo)>=4:
                    addTo=wfInfo[3]
                    #pad with 0
                    while len(addTo)!=len(stepList):
                        addTo.append(0)

            name=wfName
            # separate suffixes by + because show() excludes first part of name
            if len(wfKey)>0:
                name = name+'+'+wfKey
                if len(wfSuffix)>0: name = name+wfSuffix
            stepIndex=0
            ranStepList=[]

            fromInput={}
            #first resolve INPUT possibilities
            if num in fromInput:
                ilevel=fromInput[num]
                #print num,ilevel
                for (stepIr,step) in enumerate(reversed(stepList)):
                    stepName=step
                    stepI=(len(stepList)-stepIr)-1
                    #print stepIr,step,stepI,ilevel                    
                    if stepI>ilevel:
                        #print "ignoring"
                        continue
                    if stepI!=0:
                        testName='__'.join(stepList[0:stepI+1])+'INPUT'
                    else:
                        testName=step+'INPUT'
                    #print "JR",stepI,stepIr,testName,stepList
                    if testName in self.alcavalModule.steps:
                        #print "JR",stepI,stepIr
                        stepList[stepI]=testName
                        #pop the rest in the list
                        #print "\tmod prepop",stepList
                        for p in range(stepI):
                            stepList.pop(0)
                        #print "\t\tmod",stepList
                        break
            for (stepI,step) in enumerate(stepList):
                stepName=step
                if self.alcavalModule.steps[stepName] is None:
                    continue         
                #replace stepName is needed
                #if stepName in self.replaceStep
                if len(name) > 0 : name += '+'
                #any step can be mirrored with INPUT
                ## maybe we want too level deep input
                """
                if num in fromInput:
                    if step+'INPUT' in self.alcavalModule.steps.keys():
                        stepName = step+"INPUT"
                        stepList.remove(step)
                        stepList.insert(stepIndex,stepName)
                """
                stepNameTmp = stepName
                if len(wfKey)>0: stepNameTmp = stepNameTmp.replace('_'+wfKey,"")
                if len(wfSuffix)>0: stepNameTmp = stepNameTmp.replace(wfSuffix,"")
                name += stepNameTmp
                if addCom and (not addTo or addTo[stepIndex]==1):
                    from Configuration.PyReleaseValidation.alcaval_steps import merge
                    copyStep=merge(addCom+[self.makeStep(self.alcavalModule.steps[stepName],stepOverrides)])
                    cfg, input, opts = self.makeCmd(copyStep)
                else:
                    cfg, input, opts = self.makeCmd(self.alcavalModule.steps[stepName])

                if input and cfg :
                    msg = "FATAL ERROR: found both cfg and input for workflow "+str(num)+' step '+stepName
                    raise MatrixException(msg)

                if input:
                    cmd = input
                    pass
                else:
                    if cfg:
                        cmd  = 'cmsDriver.py '+cfg+' '+opts
                    else:
                        cmd  = 'cmsDriver.py step'+str(stepIndex+1)+' '+opts
                    if self.wm:
                        cmd+=' --io %s.io --python %s.py'%(stepName,stepName)
                    # if self.addCommand:
                    #     if self.apply:
                    #         if stepIndex in self.apply or stepName in self.apply:
                    #             cmd +=' '+self.addCommand
                    #     else:
                    #       cmd +=' '+self.addCommand
                    if self.wm and self.revertDqmio=='yes':
                        cmd=cmd.replace('DQMIO','DQM')
                        cmd=cmd.replace('--filetype DQM','')
                commands.append(cmd)
                ranStepList.append(stepName)
                stepIndex+=1
                
            self.workFlowSteps[(num,prefix)] = (num, name, commands, ranStepList)
        return
    def prepare(self, useInput=None, refRel='', fromScratch=None):
        
        for matrixFile in self.files:
            if self.what != 'all' and not any('_'+el in matrixFile for el in self.what.split(",")):
                print("ignoring non-requested file",matrixFile)
                continue
            if self.what == 'all' and not self.filesDefault[matrixFile]:
                print("ignoring",matrixFile,"from default matrix")
                continue
            
            try:
                self.collectSteps(matrixFile)
            except Exception as e:
                print("ERROR reading file:", matrixFile, str(e))
                raise
            
            try:
                self.createWorkFlows(matrixFile)
            except Exception as e:
                print("ERROR creating workflows :", str(e))
                raise
    def createWorkFlows(self, fileNameIn):

        prefixIn = self.filesPrefMap[fileNameIn]

        # get through the list of items and update the requested workflows only
        keyList = self.workFlowSteps.keys()
        ids = []
        for item in keyList:
            id, pref = item
            if pref != prefixIn : continue
            ids.append(id)
        ids.sort()
        for key in ids:
            val = self.workFlowSteps[(key,prefixIn)]
            num, name, commands, stepList = val
            nameId = str(num)+'_'+name
            if nameId in self.nameList:
                print("==> duplicate name found for ", nameId)
                print('    keeping  : ', self.nameList[nameId])
                print('    ignoring : ', val)
            else:
                self.nameList[nameId] = val

            self.workFlows.append(WorkFlow(num, name, commands=commands))

        return
    def show(self, selected=None, extended=True, cafVeto=True):

        self.showWorkFlows(selected, extended, cafVeto)
        print('\n','-'*80,'\n')
    def workFlowsByLocation(self, cafVeto=True):
        # Check if we are on CAF
        onCAF = False
        if 'cms/caf/cms' in os.environ['CMS_PATH']:
            onCAF = True

        workflows = []
        for workflow in self.workFlows:
            # if isinstance(workflow.cmds[0], InputInfo):
            #     if cafVeto and (workflow.cmds[0].location == 'CAF' and not onCAF):
            #         continue
            workflows.append(workflow)

        return workflows
    def showWorkFlows(self, selected=None, extended=True, cafVeto=True):
        if selected: selected = list(map(float,selected))
        wfs = self.workFlowsByLocation(cafVeto)
        maxLen = 100 # for summary, limit width of output
        fmt1   = "%-6s %-35s [1]: %s ..."
        fmt2   = "       %35s [%d]: %s ..."
        print("\nfound a total of ", len(wfs), ' workflows:')
        if selected:
            print("      of which the following", len(selected), 'were selected:')
        #-ap for now:
        maxLen = -1  # for individual listing, no limit on width
        fmt1   = "%-6s %-35s [1]: %s " 
        fmt2   = "       %35s [%d]: %s"

        N=[]
        for wf in wfs:
            if selected and float(wf.numId) not in selected: continue
            if extended: print('')
            #pad with zeros
            for i in range(len(N),len(wf.cmds)):                N.append(0)
            N[len(wf.cmds)-1]+=1
            wfName, stepNames = wf.nameId.split('+',1)
            for i,s in enumerate(wf.cmds):
                if extended:
                    if i==0:
                        print(fmt1 % (wf.numId, stepNames, (str(s)+' ')[:maxLen]))
                    else:
                        print(fmt2 % ( ' ', i+1, (str(s)+' ')[:maxLen]))
                else:
                    print("%-6s %-35s "% (wf.numId, stepNames))
                    break
        print('')
        for i,n in enumerate(N):
            if n:            print(n,'workflows with',i+1,'steps')

        return   
