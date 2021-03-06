
import re

# ================================================================================

class WorkFlow(object):

    def __init__(self, num, nameID, inputInfo=None, commands=None):

        self.numId  = num
        self.nameId = nameID
        self.cmds = []

        if commands:
            for (i,c) in enumerate(commands):
                nToRun=10 + (i!=0)*90
                self.check(c,nToRun)
        

        # run on real data requested:
        self.input = inputInfo

        return

    def check(self, cmd=None, nEvtDefault=10):
        if not cmd : return None

        if (isinstance(cmd,str)) and ( ' -n ' not in cmd):
            cmd+=' -n '+str(nEvtDefault)+' '

        self.cmds.append(cmd)
        return cmd