import ROOT

class NtupleChain:
    
    def __init__(self, treeName, files, buffer=None):
        
        self.treeName = treeName
        if type(files) is not list:
            files = [files]
        self.files = files
        self.buffer = buffer
        if self.buffer:
            for name,value in self.buffer.items():
                if name not in dir(self):
                    setattr(self,name,value)
        self.weight = 1.
        self.tree = None
        self.file = None
        self.entry = 0
        self.entries = 0
        self.initNBranches = -1
        
    def _initialize(self):

        if self.tree != None:
            self.tree = None
            self.file.Close()
        if len(self.files) > 0:
            fileName = self.files.pop()
            self.file = ROOT.TFile.Open(fileName)
            if not self.file:
                raise RuntimeError("Could not open file %s"%(fileName))
            self.tree = self.file.Get(self.treeName)
            if not self.tree:
                raise RuntimeError("Tree %s does not exist in file %s"%(self.treeName,fileName))
            # Buggy D3PD:
            nBranches = len(self.tree.GetListOfBranches())
            if self.initNBranches == -1:
                self.initNBranches = nBranches
            if nBranches == 0:
                # Try the next file:
                print "WARNING: skipping tree with no branches in file %s"%fileName
                return self._initialize()
            if nBranches != self.initNBranches:
                # Try the next file:
                print "WARNING: skipping tree with different number of branches (%i) in file %s"%(nBranches,fileName)
                return self._initialize()
            self.entry = 0
            self.entries = self.tree.GetEntries()
            if self.buffer != None:
                self.tree.SetBranchStatus("*",False)
                for branch,address in self.buffer.items():
                    if not self.tree.GetBranch(branch):
                        for branch in self.tree.GetListOfBranches():
                            print branch.GetName()
                        raise RuntimeError("Branch %s was not found in tree %s in file %s"%(branch,self.treeName,fileName))
                    self.tree.SetBranchStatus(branch,True)
                    self.tree.SetBranchAddress(branch,address)
            return True
        return False
    
    def read(self):
        
        if not self.entry < self.entries:
            if not self._initialize():
                return False
        self.tree.GetEntry(self.entry)
        self.weight = self.tree.GetWeight()
        self.entry += 1
        return True
