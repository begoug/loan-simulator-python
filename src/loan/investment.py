# coding: utf-8
import numpy as np
class Investment:
    def __init__(self,contribution=None):
        self._yields = {}
        self._monthly_cashflow = None
        self._monthly_estate_net_revenue = None
        self.loans       = []
        self.properties  = []
        self.fiscalities = []
        if not contribution:
            self.contribution = 0.
        else:
            self.contribution = contribution

    @property
    def has_contribution(self) :
        return self.contribution > 0.

    def compute(self):
        self.compute_payments()
        self.compute_cashflow()
        self.compute_estate_net_revenue()
        self.compute_yields()

    def compute_payments(self):
        """Updates loans monthly data using properties disbursments

        Loop
        """
        all_disbursments = sum([_.disbursments for _ in self.properties],[])
        # concatenate disbursments of all properties
        full_disbursments = []
        for month in range(self.mterm):
            names = []
            curr_disb = {'pmt':0, 'name': '', 'mterm':month}
            for disb in all_disbursments:
                if disb['mterm'] == month:
                    curr_disb['pmt'] += disb['pmt']
                    names.append(curr_disb['name'])
            if curr_disb['pmt'] > 0:
                curr_disb['name'] = '+'.join(names)
                full_disbursments.append(curr_disb)

        if len(full_disbursments)>0:
            i_loan           = 0
            lastLoan         = len(self.loans)-1
            localDisb        = []
            contributionDisb = []
            lastDisb         = len(full_disbursments)-1
            contribLeft      = self.contribution
            for i_disb,disbursment in enumerate(full_disbursments):
                disb_pmt  = disbursment['pmt']
                disb_name = disbursment['name']
                disb_term = disbursment['mterm']
                # if we have access to contribution, use it
                if contribLeft >0.:
                    contribPmt = min(contribLeft,disb_pmt)
                    contribLeft -= contribPmt
                    disb_pmt -= contribPmt
                # if the contribution was not enough, disb_pmt is greater than 0
                if disb_pmt>0.:
                    # what we already added
                    totLocalDisb = sum([disb['pmt'] for disb in localDisb])
                    # what we can take from current loan : principal - (what we already added)
                    princLeft = self.loans[i_loan].principal - totLocalDisb
                    if abs(disb_pmt-princLeft)<1e-5:disb_pmt = princLeft
                    # if there is enough principal in the loan: add this disbursment
                    # else break the disbursment: one part in current loan, the rest in the next
                    #        compute the current loan and move to the next one
                    #        do so as long as the amount left of the current disbursment is higher than the loan's prncipal
                    if princLeft>= disb_pmt:
                        localDisb.append({'name':disb_name,'pmt':disb_pmt,'mterm':disb_term})
                    else:
                        localDisb.append({'name':disb_name,'pmt':princLeft,'mterm':disb_term})
                        self.loans[i_loan].update_monthly_data(disbursments=localDisb)
                        disb_pmt -= princLeft
                        # if the next loan is not enough, use as many as necessary
                        #   in the end of this section, i_loan is the next loan that should be used
                        if i_loan<lastLoan:
                            while i_loan<lastLoan and disb_pmt > self.loans[i_loan+1].principal:
                                i_loan += 1
                                localDisb = [{'name':disb_name,'pmt':self.loans[i_loan].principal,'mterm':disb_term}]
                                disb_pmt -= self.loans[i_loan].principal
                                self.loans[i_loan].update_monthly_data(disbursments=localDisb)
                                # at this point, loan i_loan has no principal left
                            i_loan += 1
                            localDisb = [{'name':disb_name,'pmt':disb_pmt,'mterm':disb_term}]
                    # if this was the last disbursment, compute the loan
                    if i_disb == lastDisb :
                        self.loans[i_loan].update_monthly_data(disbursments=localDisb)
        else:
            for l in self.loans : l.update_monthly_data()

    @property
    def yterm(self):
        """int: maximum term of loans in years """
        return self.mterm//12

    @property
    def mterm(self):
        """int: maximum term of loans in months """
        return max([l.mterm for l in self.loans])

    def add_loan(self,loan):
        """Adds a single loan to the list of loans
        Parameters:
        -----------
        loan: `:obj:Loan`
            The loan to be added to the project
        """
        self.loans.append(loan)

    def add_property(self,property_):
        """Adds a single property to the list of properties
        Parameters:
        -----------
        property_: `:obj:Estate`
            The property to be added to the project
        """
        self.properties.append(property_)

    def add_properties(self,properties):
        """Adds a several properties to the list of properties
        Parameters:
        -----------
        properties: list of `:obj:Estate`
            The properties to be added to the project
        """
        for property_ in properties:
            self.add_property(property_)

    def addFiscality(self,fiscality):
        self.fiscalities.append(fiscality)

    @property
    def net_price(self):
        return sum( [p.net_price for p in self.properties] )

    @property
    def gross_price(self):
        return sum( [p.gross_price for p in self.properties] )

    def sell_price(self,m):
        return sum( [p.sell_price(m) for p in self.properties] )

    @property
    def funds(self):
        val =  self.contribution
        val += sum( [l.principal for l in self.loans] )
        return val

    @property
    def price_left(self):
        """float: acquisition cost left after all loans and contribution have been used"""
        return self.net_price - self.funds

    def loan_by_name(self,name):
        return [l for l in self.loans if l.name == name][0]

    def fiscBalance(self,m):
        return sum( [f.balance(m) for  f in self.fiscalities] )

    def get_monthly_data(self, key):
        # create array of size (nb_loans, nb_months) and then sum over first axis
        work_arr = np.stack([loan.get_monthly_data(key) for loan in self.loans], axis=0)
        return np.sum(work_arr, axis=0)

    @property
    def PMT(self):
        return self.get_monthly_data('PMT')

    @property
    def IPMT(self):
        return self.get_monthly_data('IPMT')

    @property
    def PPMT(self):
        return self.get_monthly_data('PPMT')

    @property
    def TPMT(self):
        return self.get_monthly_data('TPMT')

    @property
    def INS(self):
        return self.get_monthly_data('INS')

    @property
    def cashflow(self):
        return self._monthly_cashflow

    @property
    def estate_net_revenue(self):
        return self._monthly_estate_revenue

    def yield_(self, type_='net'):
        return self._yields[type_]

    def compute_cashflow(self):
        cashflow = np.zeros(self.mterm+1)
        for month in range(self.mterm+1):
            for prop in self.properties:
                cashflow[month] += prop.monthly_net_revenue(month)
            for loan in self.loans:
                cashflow[month] -= loan.TPMT[month]
        self._monthly_cashflow = cashflow.copy()
            
    def compute_estate_net_revenue(self):
        out = np.zeros(self.mterm+1)
        for month in range(self.mterm+1):
            for prop in self.properties:
                out[month] += prop.monthly_net_revenue(month)
        self._monthly_estate_revenue = out.copy()

    def compute_yields(self):
        net   = np.empty(self.yterm)
        netnet= np.empty(self.yterm)
        gross = np.empty(self.yterm)
        # gross yield
        operation_cost = self.gross_price
        for year in range(self.yterm):
            net_revenue = 0.
            gross_revenue = 0.
            total_payment = 0.
            total_interests = 0.
            loan_cost = 0.
            fiscality = 0.
            mstart = int(year*12.+1)
            mstop = int(mstart+12-1)
            for month in range(mstart, mstop):
                for prop in self.properties:
                    net_revenue += prop.monthly_net_revenue(month)
                    gross_revenue += prop.monthly_gross_revenue(month)
                for loan in self.loans:
                    total_interests += loan.IPMT[month]
                    total_payment += loan.TPMT[month]
                    loan_cost += loan.IPMT[month] + loan.INS[month]
            fiscality += (0.3+0.18)*gross_revenue
            fiscality -= 0.3*total_interests
            net[year] = (net_revenue -loan_cost)/operation_cost
            netnet[year] = (net_revenue -loan_cost-fiscality)/operation_cost
            gross[year] += gross_revenue/operation_cost
        self._yields['net'] = net.copy()*100.
        self._yields['gross'] = gross.copy()*100.
        self._yields['netnet'] = netnet.copy()*100.
        
            
    # == #def leftCap(self,m):
    # == #    return self.funds - self.cumulPPMT(m)
    # == #def propCost(self,m): return sum([p.monthlyCost(m) for p in self.properties])
    # == #def propRevenue(self,m):return sum([p.monthlyRevenue(m) for p in self.properties])

    # == #def balance(self,m):
    # == #    # property cost and revenue
    # == #    propCost    = 0.
    # == #    propRevenue = 0.
    # == #    for p in self.properties:
    # == #        propCost    += sum( [ p.monthlyCost(n+1)    for n in range(m) ] )
    # == #        propRevenue += sum( [ p.monthlyRevenue(n+1) for n in range(m) ] )
    # == #    # loan cost to reimbourse
    # == #    loanCost =  self.cumulIPMT(m) + self.leftCap(m) + self.cumulIns(m)
    # == #    # fiscalities balance
    # == #    cumulFiscBalance    = sum( [ self.fiscBalance(n+1)    for n in range(m) ] )
    # == #    return propRevenue + self.sellPrice(m) - propCost - loanCost + cumulFiscBalance

    # == #def monthly_cost(self,m):
    # == #    return self.totPMT(m) + self.propCost(m)

