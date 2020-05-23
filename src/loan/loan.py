import numpy as np

class Loan(object):
    """Loan class manages loans

    Parameters
    ----------
    yterm: int
        Total length of loan
    nominal_rate: float
    principal: float
    insurace: float
    name: str
    ydeff: int
    compute_now: bool
    """
    MONTHLY_KEYS = [
            'PMT', # total payment (principal+interests)
            'PPMT', # principal
            'IPMT', # interests
            'TPMT', # total payment (incl. insurance)
            'INS', # insurance
    ]
    # CONVENTIONS FOR THIS CLASS:
    #    - month m is in 0..mtermtermnth 0 at beginning of loan)
    def __init__(self, yterm=None, nominal_rate=None, principal=None, ins_rate=None, name='', ydeff=0, compute_now=True):
        self.yterm = yterm
        self.mterm = int(self.yterm*12)
        self.nominal_rate = nominal_rate
        # actuariel
        self.eff_rate  = ((1+self.nominal_rate/100.)**(1./12.)-1)*100.
        # proportionel
        #self.eff_rate  = self.nominal_rate/12.
        self.principal      = principal
        self.ins_rate      = ins_rate if ins_rate else 0.
        self.name  = name
        self.mdeff = int(ydeff*12)
        self.ydeff = ydeff
        self.obtained = principal
        self._monthly_data = {}
        if compute_now :
            self.update_monthly_data()

    def get_monthly_data(self, key):
        return self._monthly_data[key]

    @property
    def PMT(self):
        return self.get_monthly_data('PMT')

    @property
    def PPMT(self):
        return self.get_monthly_data('PPMT')

    @property
    def IPMT(self):
        return self.get_monthly_data('IPMT')

    @property
    def TPMT(self):
        return self.get_monthly_data('TPMT')

    @property
    def INS(self):
        return self.get_monthly_data('INS')

    @property
    def PLFT(self):
        return self.get_monthly_data('PLFT')

    @property
    def total_cost(self):
     return self._monthly_data['cumul_IPMT'][-1] + self._monthly_data['cumul_INS'][-1]

    @property
    def total_ins(self):
     return self._monthly_data['cumul_INS'][-1]

    @property
    def total_int(self):
     return self._monthly_data['cumul_IPMT'][-1]

    def cPMT(self,month):
        """Computes monthly payment of principal
        """
        Pv   = self.principal
        rate = self.eff_rate/100.
        Nper = self.mterm-self.mdeff
        #print(f'Compute PMT: {Pv}, {rate}, {Nper}')
        if rate>1e-8:
            PMT  = (Pv*rate)/(1.-(1.+rate)**(-Nper))
        else:
            PMT  = (Pv)/Nper
        return PMT

    def cInsFees(self,month):
        return self.ins_rate/100./12.*self.principal

    def cTotPMT(self,month):
        return self.cInsFees(month)+self.cPMT(month)

    def update_monthly_data(self, disbursments=None, term=None):
        term = term or self.mterm
        disbursments = disbursments if disbursments else [{'name': 'full loan', 'pmt':self.principal , 'mterm':0}]
        #print('='*25+self.name + ' '+str(self.principal))
        #print('\n'.join(['{name:<20}: {pmt:>15.2f} au mois numero {term:>3d}'.format(name=dec['name'],pmt=dec['pmt'],term=dec['mterm']) for dec in disbursments]))
        # prepare monthly payments and interests
        for key in ['IPMT', 'PPMT', 'PMT', 'PLFT', 'INS', 'TPMT']:
            self._monthly_data[key] = np.zeros(term+1)
        self._monthly_data['PLFT'][0] = self.principal
        # prepare variables:
        # * rate
        # * obtained: amount made availablen (accounts for disbusrments)
        # * left: principal left 
        rate  = self.eff_rate/100.
        obtained = 0.
        left = self.principal
        # only fill out data for this month, if month is higher thant self.mterm, intialization to 0 is used
        for month in range(1, self.mterm+1):
            # get all disbursments made the previous month
            last_obtained = sum([disb['pmt'] for disb in disbursments if disb['mterm'] == month-1])
            # update obtained amount
            obtained += last_obtained
            if month<=self.mdeff:
                interests = obtained * rate
                payment = interests
                principal = 0.
            else:
                interests = left * rate
                payment = self.cPMT(month)
                principal = payment-interests
            left -= principal
            insurance = self.cInsFees(month)
            #store
            self._monthly_data['PMT'][month] = payment
            self._monthly_data['IPMT'][month] = interests
            self._monthly_data['PPMT'][month] = principal
            self._monthly_data['INS'][month] = insurance
            self._monthly_data['TPMT'][month] = payment + insurance
            self._monthly_data['PLFT'][month] = left
            self._monthly_data['INS'][month] = self.cInsFees(month)
        # compute cumulative sums
        for key in ['PPMT', 'IPMT', 'PMT', 'INS', 'TPMT']:
            self._monthly_data['cumul_'+key] = np.cumsum(self._monthly_data[key])

