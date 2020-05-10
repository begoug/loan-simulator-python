import numpy as np

class Loan(object):
    MONTHLY_KEYS = [
            'PMT', # total payment (principal+interests)
            'PPMT', # principal
            'IPMT', # interests
            'TPMT', # total payment (incl. insurance)
            'INS', # insurance
    ]
    # CONVENTIONS FOR THIS CLASS:
    #    - month m is in 0..mtermtermnth 0 at beginning of loan)
    def __init__(self,termY=None,nominalRate=None,principal=None,insurance=None,name='',deffY=0, computeNow=True):
        self.termY          = termY
        self.mterm          = int(self.termY*12)
        self.nominalRate    = nominalRate
        # actuariel
        self.eff_rate  = ((1+self.nominalRate/100.)**(1./12.)-1)*100.
        # proportionel
        #self.eff_rate  = self.nominalRate/12.
        self.principal      = principal
        self.insurance      = insurance if insurance else 0.
        self.name  = name
        self.deffM = int(deffY*12)
        self.deffY = deffY
        self.obtained = principal
        self._monthly_data = {}
        if computeNow :
            self.update_monthly_data()
    #@property
    #def PMT(self):
    #    try:
    #        return self._PMT
    #    except AttributeError:
    #        Pv   = self.principal
    #        rate    = self.rate
    #        Nper = self.termMois

    def cPMT(self,month):
        """Compute monthly payment of principal
        """
        Pv   = self.principal
        rate    = self.eff_rate/100.
        Nper = self.mterm-self.deffM
        if rate>1e-8:
            PMT  = (Pv*rate)/(1.-(1.+rate)**(-Nper))
        else:
            PMT  = (Pv)/Nper
        return PMT

    def cInsFees(self,month):
        return self.insurance/float(self.mterm)
    def cTotPMT(self,month):
        return self.cInsFees(month)+self.cPMT(month)

    def getTotPMT   (self,month):
        return self._totPMT[month] if month <=self.mterm else 0.
    def getInsFees  (self,month):
        return self._insFees  [month] if month <=self.mterm else 0.
    def getPMT      (self,month):
        return self._PMT[month] if month <=self.mterm else 0.
    def getIPMT     (self,month) : return self._IPMT     [month] if month <=self.mterm else 0.
    def getPPMT     (self,month) : return self._PPMT     [month] if month <=self.mterm else 0.
    def getPleft    (self,month) : return self._Pleft    [month] if month <=self.mterm else 0.
    def getCumulPPMT(self,month) : return self._cumulPPMT[min(month,self.mterm)]
    def getCumulIPMT(self,month) : return self._cumulIPMT[min(month,self.mterm)]
    def getCumulPMT (self,month) : return self._cumulPMT [min(month,self.mterm)]
    def getCumulIns (self,month) : return self._cumulIns [min(month,self.mterm)]

    def update_monthly_data(self,disbursments=None):
        disbursments = disbursments if disbursments else [{'pmt':self.principal , 'mterm':0}]
        print('='*25+self.name + ' '+str(self.principal))
        print('\n'.join(['{name:<20}: {pmt:>15.2f} au mois numero {term:>3d}'.format(name=dec['name'],pmt=dec['pmt'],term=dec['mterm']) for dec in disbursments]))
        # prepare monthly payments and interests
        for key in ['IPMT', 'PPMT', 'PMT', 'PLFT', 'INS']:
            self._monthly_data[key] = np.zero(self.mterm+1)
        self._monthly_data['PLFT'][0] = self.principal
        # prepare variables:
        # * rate
        # * obtained: amount made availablen (accounts for disbusrments)
        # * left: principal left 
        rate  = self.eff_rate/100.
        obtained = 0.
        left = self.principal
        for month in range(1,self.mterm+1):
            # get all disbursments made the previous month
            last_obtained = sum([disb['pmt'] for disb in disbursments if disb['mterm'] == month-1])
            # update obtained amount
            obtained += last_obtained
            if month<=self.deffM:
                interests = obtained * rate
                payment = interests
                principal = 0.
            else:
                interests = left * rate
                payment = self.cPMT(month)
                principal = payment-interests
            left -= principal
            self._monthly_data['INS'][month] = self.cInsFees(month)
            #store
            self._monthly_data['PMT'][month] = payment
            self._monthly_data['IPMT'][month] = interests
            self._monthly_data['PPMT'][month] = principal
            self._monthly_data['PLFT'][month] = left
            self._monthly_data['INS'][month] = self.cInsFees(month)
        # compute cumulative sums
        self._totPMT    = [ self._insFees[month]+self._PMT[month] for month in range(self.mterm+1)]
        for key in ['PPMT', 'IPMT', 'PMT', 'INS']:
            self._monthly_data['cumul_'+key] = np.cumsum(self._monthly_data[key])

