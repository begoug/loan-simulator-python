# coding: utf-8
class Investment:
    def __init__(self,contribution=None):
        self.loans       = []
        self.properties  = []
        self.fiscalities = []
        if not contribution:
            self.contribution = 0.
        else:
            self.contribution = contribution
    @property
    def hasContribution(self) :
        return self.contribution > 0.

    def compute(self):
        if self.properties[0].hasDisbursments:
            disbursments     = self.properties[0].disbursments
            i_loan           = 0
            lastLoan         = len(self.loans)-1
            localDisb        = []
            contributionDisb = []
            lastDisb         = len(disbursments)-1
            contribDisb      = []
            contribLeft      = self.contribution
            for i_disb,disbursment in enumerate(disbursments):
                currDisbPmt  = disbursment['pmt']
                currDisbName = disbursment['name']
                currDisbTerm = disbursment['mterm']
                # if we have access to contribution, use it
                if contribLeft >0.:
                    contribPmt = min(contribLeft,currDisbPmt)
                    contribDisb.append({'name':currDisbName , 'pmt':contribPmt  , 'mterm':currDisbTerm})
                    contribLeft -= contribPmt
                    currDisbPmt -= contribPmt
                # if the contribution was not enough, currDisbPmt is greater than 0
                if currDisbPmt>0.:
                    # what we already added
                    totLocalDisb = sum([disb['pmt'] for disb in localDisb])
                    # what we can take from current loan : principal - (what we already added)
                    princLeft = self.loans[i_loan].principal - totLocalDisb
                    if abs(currDisbPmt-princLeft)<1e-5:currDisbPmt = princLeft
                    # if there is enough principal in the loan: add this disbursment
                    # else break the disbursment: one part in current loan, the rest in the next
                    #        compute the current loan and move to the next one
                    #        do so as long as the amount left of the current disbursment is higher than the loan's prncipal
                    if princLeft>= currDisbPmt:
                        localDisb.append({'name':currDisbName,'pmt':currDisbPmt,'mterm':currDisbTerm})
                    else:
                        localDisb.append({'name':currDisbName,'pmt':princLeft,'mterm':currDisbTerm})
                        self.loans[i_loan].computeMonthly(disbursments=localDisb)
                        currDisbPmt -= princLeft
                        # if the next loan is not enough, use as many as necessary
                        #   in the end of this section, i_loan is the next loan that should be used
                        if i_loan<lastLoan:
                            while i_loan<lastLoan and currDisbPmt > self.loans[i_loan+1].principal:
                                i_loan += 1
                                localDisb = [{'name':currDisbName,'pmt':self.loans[i_loan].principal,'mterm':currDisbTerm}]
                                currDisbPmt -= self.loans[i_loan].principal
                                self.loans[i_loan].computeMonthly(disbursments=localDisb)
                                # at this point, loan i_loan has no principal left
                            i_loan += 1
                            localDisb = [{'name':currDisbName,'pmt':currDisbPmt,'mterm':currDisbTerm}]
                    # if this was the last disbursment, compute the loan
                    if i_disb == lastDisb :
                        self.loans[i_loan].computeMonthly(disbursments=localDisb)
        else:
            for l in self.loans : l.computeMonthly()
    @property
    def termY(self): return max([l.termY for l in self.loans])
    def mterm(self): return max([l.mterm for l in self.loans])
    def addLoan(self,loan):
        self.loans.append(loan)

    def addProperty(self,property_):
        self.properties.append(property_)

    def addProperties(self,properties):
        for property_ in properties:
            self.addProperty(property_)

    def addFiscality(self,fiscality):
        self.fiscalities.append(fiscality)

    @property
    def acqCost(self):
        return sum( [p.acqCost for p in self.properties] )
    @property
    def acqGrossCost(self):
        return sum( [p.acqGrossCost for p in self.properties] )

    def sellPrice(self,m):
        return sum( [p.sellPrice(m) for p in self.properties] )

    @property
    def funds(self):
        val =  self.contribution
        val += sum( [l.principal for l in self.loans] )
        return val

    @property
    def costLeft(self):
        return self.acqCost - self.funds

    def getLoanByName(self,name):
        return [l for l in self.loans if l.name == name][0]
    def fiscBalance(self,m):
        return sum( [f.balance(m) for  f in self.fiscalities] )
    def insFees(self,m)  : return sum( [ l.getInsFees(m)   for l in self.loans] )
    def PMT(self,m)      : return sum( [ l.getPMT(m)       for l in self.loans] )
    def IPMT(self,m)     : return sum( [ l.getIPMT(m)      for l in self.loans] )
    def totPMT(self,m)   : return sum( [ l.getTotPMT(m)    for l in self.loans] )
    def cumulPPMT(self,m): return sum( [ l.getCumulPPMT(m) for l in self.loans] )
    def cumulIPMT(self,m): return sum( [ l.getCumulIPMT(m) for l in self.loans] )
    def cumulIns(self,m) : return sum( [ l.getCumulIns(m)  for l in self.loans] )
    def leftCap(self,m):
        return self.funds - self.cumulPPMT(m)
    def propCost(self,m): return sum([p.monthlyCost(m) for p in self.properties])
    def propRevenue(self,m):return sum([p.monthlyRevenue(m) for p in self.properties])
    def balance(self,m):
        # property cost and revenue
        propCost    = 0.
        propRevenue = 0.
        for p in self.properties:
            propCost    += sum( [ p.monthlyCost(n+1)    for n in range(m) ] )
            propRevenue += sum( [ p.monthlyRevenue(n+1) for n in range(m) ] )
        # loan cost to reimbourse
        loanCost =  self.cumulIPMT(m) + self.leftCap(m) + self.cumulIns(m)
        # fiscalities balance
        cumulFiscBalance    = sum( [ self.fiscBalance(n+1)    for n in range(m) ] )
        return propRevenue + self.sellPrice(m) - propCost - loanCost + cumulFiscBalance
    def monthlyCost(self,m):
        return self.totPMT(m) + self.propCost(m)

