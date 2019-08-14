# coding: utf-8
"""This module provides the Estate class
"""
class Estate:
    def __init__(self,\
            acqGrossCost=None,\
            realtorRate =0.0 ,\
            notaryRate  =0.0 ,\
            sellRate    =0.0 ,\
            rent        =None,\
            propertyTax =0.0 ,\
            localTax    =0.0 ,\
            vacancy     =None,\
            use='principal'  ,\
            condoFees   =0.0 ,\
            disbursments=None,
            delivery    =0   ,
            construction = 0):
        self.acqGrossCost   = acqGrossCost
        self.realtorRate    = realtorRate
        self.notaryRate     = notaryRate
        self.sellRate       = sellRate
        self.acqRealtorCost = self.acqGrossCost*(1.+self.realtorRate/100.)
        self.rent           = rent
        self.propertyTax    = propertyTax
        self.localTax       = localTax
        self.use            = use
        self.condoFees      = condoFees
        self.hasDisbursments = disbursments is not None
        self._disbursments   = disbursments
        self.delivery        = int(delivery*12)
        self.construction    = construction
    @property
    def acqCost(self):
        return self.acqGrossCost*(1.+self.realtorRate/100. + self.notaryRate/100.) + self.construction
    @property
    def disbursments(self):
        out=[]
        for i,disb in enumerate(self._disbursments):
            out.append({'name':disb['name'],'termM':disb['termM']});
            pmt = self.acqGrossCost *disb['rate']/100.
            if i == 0:pmt += self.acqGrossCost*(self.realtorRate+self.notaryRate)/100.
            out[-1].update({'pmt':pmt})
        return  out
    def sellPrice(self,m):
        return ((self.acqGrossCost+self.construction)*(1-0.1)) * (1.+self.sellRate/100.)**(m/12)
    def monthlyCost(self,m):
        if  m > self.delivery :
            if self.use == 'principal':
                return self.condoFees/12. + self.propertyTax/12.
        else: return 0.
    def monthlyRevenue(self,m):
        if self.use == 'principal':
            return 0.
        else:
            return self.rent
