class Loan(object):
    # CONVENTIONS FOR THIS CLASS:
    #    - month m is in 0..termM (month 0 at beginning of loan)
    def __init__(self,termY=None,nominalRate=None,principal=None,insurance=None,name='',deffY=0, computeNow=True):
        self.termY          = termY
        self.termM          = int(self.termY*12)
        self.nominalRate    = nominalRate
        # actuariel
        self.effectiveRate  = ((1+self.nominalRate/100.)**(1./12.)-1)*100.
        # proportionel
        #self.effectiveRate  = self.nominalRate/12.
        self.principal      = principal
        self.insurance      = insurance if insurance else 0.
        self.name  = name
        self.deffM = int(deffY*12)
        self.deffY = deffY
        self.obtained = principal
        if computeNow :
            self.computeMonthly()
    #@property
    #def PMT(self):
    #    try:
    #        return self._PMT
    #    except AttributeError:
    #        Pv   = self.principal
    #        r    = self.rate
    #        Nper = self.termMois

    def cPMT(self,m):
        Pv   = self.principal
        r    = self.effectiveRate/100.
        Nper = self.termM-self.deffM
        if r>1e-8:
            PMT  = (Pv*r)/(1.-(1.+r)**(-Nper))
        else:
            PMT  = (Pv)/Nper
        return PMT

    def cInsFees(self,m):
        return self.insurance/float(self.termM)
    def cTotPMT(self,m):
        return self.cInsFees(m)+self.cPMT(m)

    def getTotPMT   (self,m) : return self._totPMT   [m] if m <=self.termM else 0.
    def getInsFees  (self,m) : return self._insFees  [m] if m <=self.termM else 0.
    def getPMT      (self,m) : return self._PMT      [m] if m <=self.termM else 0.
    def getIPMT     (self,m) : return self._IPMT     [m] if m <=self.termM else 0.
    def getPPMT     (self,m) : return self._PPMT     [m] if m <=self.termM else 0.
    def getPleft    (self,m) : return self._Pleft    [m] if m <=self.termM else 0.
    def getCumulPPMT(self,m) : return self._cumulPPMT[min(m,self.termM)]
    def getCumulIPMT(self,m) : return self._cumulIPMT[min(m,self.termM)]
    def getCumulPMT (self,m) : return self._cumulPMT [min(m,self.termM)]
    def getCumulIns (self,m) : return self._cumulIns [min(m,self.termM)]

    def computeMonthly(self,disbursments=None):
        disbursments = disbursments if disbursments else [{'pmt':self.principal , 'termM':0}]
        print('='*25+self.name + ' '+str(self.principal))
        print('\n'.join(['{name:<20}: {pmt:>15.2f} au mois numero {term:>3d}'.format(name=dec['name'],pmt=dec['pmt'],term=dec['termM']) for dec in disbursments]))
        r    = self.effectiveRate/100.
        self._IPMT     = [0.            ]
        self._PPMT     = [0.            ]
        self._Pleft    = [self.principal]
        self._PMT      = [ 0.           ]
        cumulPPMT = 0.
        obtained  = 0.
        for m in range(1,self.termM+1):
            # check whether a disbursment was made the previous month
            obtainedLast = sum([disb['pmt'] for disb in disbursments if disb['termM'] == m-1])
            obtained += obtainedLast
            if m<=self.deffM:
                I = obtained * r
                M = I
                P = 0.
            else:
                I = self._Pleft[m-1] * r
                M = self.cPMT(m)
                P = M-I
            Pleft = self._Pleft[m-1] - P
            #store
            self._PMT.append(M)
            self._IPMT.append(I)
            self._PPMT.append(P)
            self._Pleft.append(Pleft)

        self._insFees   = [ self.cInsFees(m)              for m in range(self.termM+1)]
        self._totPMT    = [ self._insFees[m]+self._PMT[m] for m in range(self.termM+1)]
        self._cumulPPMT = [ sum(self._PPMT   [0:m+1])     for m in range(self.termM+1)]
        self._cumulIPMT = [ sum(self._IPMT   [0:m+1])     for m in range(self.termM+1)]
        self._cumulPMT  = [ sum(self._PMT    [0:m+1])     for m in range(self.termM+1)]
        self._cumulIns  = [ sum(self._insFees[0:m+1])     for m in range(self.termM+1)]

