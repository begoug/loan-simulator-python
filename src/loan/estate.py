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
    yearly_charges: float, optional (0.0)
        Yearly charges, such as condo/maintenance fees or insurance
    disbursments: list of dict, optional (None)
        List of dictionaries built as {'name': string, 'rate': float, 'termM': int} items
        Where:

        * name is the building stage label ('fundation', 'roof',...)
        * rate is the building stage price as a percentage of the gross price
        * termM is the building stage end starting from the begining of construction, in months
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
            yearly_charges=0.0 ,
            disbursments=None,
            delivery=0,
            construction= 0):
        self.gross_price = gross_price
        self.realtor_rate = realtor_rate
        self.notary_rate = notary_rate
        self.sell_rate = sell_rate
        self.rent = rent
        self.property_tax = property_tax
        self.local_tax = local_tax
        self.use = use
        self.yearly_charges = yearly_charges
        self.has_disbursments = disbursments is not None
        self._disbursments = disbursments
        self.delivery = int(delivery*12)
        self.construction = construction

    @property
    def full_price(self):
        price = 0.
        # gross price + fees
        for rate in [100., self.realtor_rate, self.notary_rate]:
            price += self.gross_price * rate/100.
        return self.gross_price*(1.+self.realtor_rate/100. + self.notary_rate/100.) + self.construction

    @property
    def disbursments(self):
        out=[]
        for i,disb in enumerate(self._disbursments):
            out.append({'name':disb['name'],'termM':disb['termM']});
            pmt = self.gross_price *disb['rate']/100.
            if i == 0:pmt += self.gross_price*(self.realtor_rate+self.notary_rate)/100.
            out[-1].update({'pmt':pmt})
        return  out
    def sellPrice(self,m):
        return ((self.gross_price+self.construction)*(1-0.1)) * (1.+self.sell_rate/100.)**(m/12)
    def monthlyCost(self,m):
        if  m > self.delivery :
            if self.use == 'principal':
                return self.yearly_charges/12. + self.property_tax/12.
        else: return 0.

    def monthlyRevenue(self,m):
        if self.use == 'principal':
            return 0.
        else:
            return self.rent
