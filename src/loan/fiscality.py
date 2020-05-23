# coding: utf-8
from abc import ABC
class Fiscality(ABC):
    def __init__(self):
        pass

    def yearly_tax(self, loan_interests=0., gross_revenue=0., property_management=0., loan_insurance=0., rent_insurance=0.):
        return None

class NoFiscality(Fiscality):
    def yearly_tax(self, **kwargs):
        return 0.

class French(Fiscality):
    def __init__(self):
        self.income_rate = 0.3
        self.csg_rate = 0.172

    def deductible(self, gross_revenue=0., loan_interests=0., property_management=0., loan_insurance=0., rent_insurance=0.):
        return 0.

    def yearly_tax(self, gross_revenue=0., loan_interests=0., property_management=0., loan_insurance=0., rent_insurance=0.):
        deductible = self.deductible(gross_revenue, loan_interests, property_management, loan_insurance, rent_insurance)
        net_revenue = gross_revenue - deductible
        income_tax = self.income_rate*net_revenue
        csg_tax = self.csg_rate*net_revenue
        return csg_tax+income_tax

class FoncierReel(French):
    def deductible(self, gross_revenue=0., loan_interests=0., property_management=0., loan_insurance=0., rent_insurance=0.):
        return loan_interests + property_management + loan_insurance + rent_insurance


class MicroFoncier(French):
    def __init__(self, gross_limit=15000.):
        self.gross_limit = gross_limit
        super().__init__()

    def deductible(self, gross_revenue=0., loan_interests=0., property_management=0., loan_insurance=0., rent_insurance=0.):
        out = 0.
        if gross_revenue < self.gross_limit:
            out = gross_revenue*0.3
        else:
            print(f'Warning! Micro-foncier does not apply when gross revenue is higher than {self.gross_limit}')
            out = FoncierReel.deductible(self, gross_revenue=0., loan_interests=0., property_management=0., loan_insurance=0., rent_insurance=0.)
        return gross_revenue*0.7
