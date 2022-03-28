# Copied from https://github.com/cms-sw/cmssw/

import os
# merge dictionaries, with prioty on the [0] index
def merge(dictlist,TELL=False):
    import copy
    last=len(dictlist)-1
    if TELL: print(last,dictlist)
    if last==0:
        # ONLY ONE ITEM LEFT
        return copy.copy(dictlist[0])
    else:
        reducedlist=dictlist[0:max(0,last-1)]
        if TELL: print(reducedlist)
        # make a copy of the last item
        d=copy.copy(dictlist[last])
        # update with the last but one item
        d.update(dictlist[last-1])
        # and recursively do the rest
        reducedlist.append(d)
        return merge(reducedlist,TELL)

#the class to collect all possible steps
class Steps(dict):
    def __setitem__(self,key,value):
        if key in self:
            print("ERROR in Step")
            print("overwriting",key,"not allowed")
            import sys
            sys.exit(-9)
        else:
            self.update({key:value})
            # make the python file named <step>.py
            #if not '--python' in value:                self[key].update({'--python':'%s.py'%(key,)})

    def overwrite(self,keypair):
        value=self[keypair[1]]
        self.update({keypair[0]:value})

InputInfoNDefault=2000000 
class InputInfo(object):
    def __init__(self,dataSet,dataSetParent='',label='',run=[],ls={},files=1000,events=InputInfoNDefault,split=10,location='CAF',ib_blacklist=None,ib_block=None) :
        self.run = run
        self.ls = ls
        self.files = files
        self.events = events
        self.location = location
        self.label = label
        self.dataSet = dataSet
        self.split = split
        self.ib_blacklist = ib_blacklist
        self.ib_block = ib_block
        self.dataSetParent = dataSetParent
    def __str__(self):
        if self.ib_block:
            return "input from: {0} with run {1}#{2}".format(self.dataSet, self.ib_block, self.run)
        return "input from: {0} with run {1}".format(self.dataSet, self.run)

    def das(self, das_options, dataset):
        if len(self.run) != 0 or self.ls:
            queries = self.queries(dataset)[:3]
            if len(self.run) != 0:
              command = ";".join(["dasgoclient %s --query '%s'" % (das_options, query) for query in queries])
            else:
              lumis = self.lumis()
              commands = []
              while queries:
                commands.append("dasgoclient %s --query 'lumi,%s' --format json | das-selected-lumis.py %s " % (das_options, queries.pop(), lumis.pop()))
              command = ";".join(commands)
            command = "({0})".format(command)
        else:
            command = "dasgoclient %s --query '%s'" % (das_options, self.queries(dataset)[0])
       
        # Run filter on DAS output 
        if self.ib_blacklist:
            command += " | grep -E -v "
            command += " ".join(["-e '{0}'".format(pattern) for pattern in self.ib_blacklist])
        from os import getenv
        if getenv("CMSSW_USE_IBEOS","false")=="true": return command + " | ibeos-lfn-sort"
        return command + " | sort -u"

    def lumiRanges(self):
        if len(self.run) != 0:
            return "echo '{\n"+",".join(('"%d":[[1,268435455]]\n'%(x,) for x in self.run))+"}'"
        if self.ls :
            return "echo '{\n"+",".join(('"%d" : %s\n'%( int(x),self.ls[x]) for x in self.ls.keys()))+"}'"
        return None

    def lumis(self):
      query_lumis = []
      if self.ls:
        for run in self.ls.keys():
          run_lumis = []
          for rng in self.ls[run]:
              if isinstance(rng, int):
                  run_lumis.append(str(rng))
              else:
                  run_lumis.append(str(rng[0])+","+str(rng[1]))
          query_lumis.append(":".join(run_lumis))
      return query_lumis

    def queries(self, dataset):
        query_by = "block" if self.ib_block else "dataset"
        query_source = "{0}#{1}".format(dataset, self.ib_block) if self.ib_block else dataset

        if self.ls :
            the_queries = []
            #for query_run in self.ls.keys():
            # print "run is %s"%(query_run)
            # if you have a LS list specified, still query das for the full run (multiple ls queries take forever)
            # and use step1_lumiRanges.log to run only on LS which respect your selection

            # DO WE WANT T2_CERN ?
            return ["file {0}={1} run={2}".format(query_by, query_source, query_run) for query_run in self.ls.keys()]
            #return ["file {0}={1} run={2} site=T2_CH_CERN".format(query_by, query_source, query_run) for query_run in self.ls.keys()]


                # 
                #for a_range in self.ls[query_run]:
                #    # print "a_range is %s"%(a_range)
                #    the_queries +=  ["file {0}={1} run={2} lumi={3} ".format(query_by, query_source, query_run, query_ls) for query_ls in expandLsInterval(a_range) ]
            #print the_queries
            return the_queries

        site = " site=T2_CH_CERN"
        if "CMSSW_DAS_QUERY_SITES" in os.environ:
            if os.environ["CMSSW_DAS_QUERY_SITES"]:
                site = " site=%s" % os.environ["CMSSW_DAS_QUERY_SITES"]
            else:
                site = ""
        if len(self.run) != 0:
            return ["file {0}={1} run={2}{3}".format(query_by, query_source, query_run, site) for query_run in self.run]
            #return ["file {0}={1} run={2} ".format(query_by, query_source, query_run) for query_run in self.run]
        else:
            return ["file {0}={1}{2}".format(query_by, query_source, site)]
            #return ["file {0}={1} ".format(query_by, query_source)]