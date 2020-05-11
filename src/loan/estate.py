# coding: utf-8
"""This module provides the Estate class
"""
class Estate:
    """Class Estate manages fees, taxes and delays related to a given real estate asset

    Parameters
    ----------
    gross_price: float
        Gross buying price (free of realtor and notary fees)
    realtor_rate: float, optional (0.0)
        Realtor fee as a percentage of the gross price
    notary_rate: float, optional (0.0)
        Notary fee as a percentage of the gross price
    sell_rate: float, optional (0.0)
        Estimate of value growth, percentage
    rent: float, optional (None)
        Rent received if use is 'investment', payed if use is 'principal'
    property_tax: float, optional (0.0)
        Yearly property tax
    local_tax: float, optional (0.0)
        Yearly local tax
    vacancy: float, optional (None)
        Percentage of vacancy if use is investment
    use: str, optional ('principal')
        Type of use in ['principal', 'rent', 'investment']
    yearly_fees: float, optional (0.0)
        Yearly charges, such as condo/maintenance fees
    yearly_insurance: float, optional (0.0)
        Yearly insurance fees
    disbursments: list of dict, optional (None)
        List of dictionaries built as {'name': string, 'rate': float, 'mterm': int} items
        Where:

        * name is the building stage label ('fundation', 'roof',...)
        * rate is the building stage price as a percentage of the gross price
        * mterm is the building stage end starting from the begining of construction, in months
    delivery: float, optional (0.0)
        Delivery date, in months from the begining of construction
    construction: float, optional (0.0)
        Amount invested in construction work
    """
    def __init__(self,
            gross_price=None,
            realtor_rate=0.0,
            notary_rate=0.0 ,
            sell_rate=0.0,
            rent=None,
            property_tax=0.0,
            local_tax=0.0,
            vacancy=None,
            use='principal',
            yearly_fees=0.0,
            yearly_insurance=0.0,
            disbursments=None,
            delivery=0,
            construction= 0):
        self.gross_price = gross_price
        self.realtor_rate = realtor_rate
        self.notary_rate = notary_rate
        self.sell_rate = sell_rate
        self.rent = rent
        self.yearly_insurance = yearly_insurance
        self.property_tax = property_tax
        self.local_tax = local_tax
        self.use = use
        self.yearly_fees = yearly_fees
        self.has_disbursments = disbursments is not None
        self._disbursments = disbursments
        self.delivery = int(delivery*12)
        self.construction = construction

    @property
    def net_price(self):
        price = 0.
        # gross price + fees
        for rate in [100., self.realtor_rate, self.notary_rate]:
            price += self.gross_price * rate/100.
        return self.gross_price*(1.+self.realtor_rate/100. + self.notary_rate/100.) + self.construction

    @property
    def disbursments(self):
        out=[]
        for i,disb in enumerate(self._disbursments):
            out.append({'name':disb['name'],'mterm':disb['mterm']});
            pmt = self.gross_price *disb['rate']/100.
            if i == 0:pmt += self.gross_price*(self.realtor_rate+self.notary_rate)/100.
            out[-1].update({'pmt':pmt})
        return  out

    def sell_price(self,month):
        """Returns the estimated selling price at a given month
        Paramters
        ---------
        month: int
            Current month, starting from delivery
        """
        return ((self.gross_price+self.construction)) * (1.+self.sell_rate/100.)**(month//12)

    def monthly_cost(self,month=1):
        cost = 0.
        if  month > self.delivery :
            cost+= self.yearly_insurance/12.
            if self.use == 'principal':
                cost+= self.yearly_fees/12.
                cost+= self.property_tax/12.
                cost+= self.local_tax/12.
            elif self.use == 'rent':
                cost+= self.local_tax/12.
                cost+= self.rent
            elif self.use == 'investment':
                cost+= self.yearly_fees/12.
                cost+= self.property_tax/12.
        return cost

    def monthly_gross_revenue(self,month=1):
        """Return the net revenue (rents-charges) generated at a given month
        Parameters:
        -----------
        month: int, optional (1)
            Current month starting from delivery
        """
        revenue = 0.
        if self.use == 'investment':
            revenue = self.rent
        return revenue

    def monthly_net_revenue(self,month=1):
        """Return the net revenue (rents-charges) generated at a given month
        Parameters:
        -----------
        month: int, optional (1)
            Current month starting from delivery
        """
        revenue = self.monthly_gross_revenue(month) - self.monthly_cost(month)
        return revenue
