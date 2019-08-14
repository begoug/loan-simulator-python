# coding: utf-8
class Fiscality(object):
    def __init__(self):
        self.advantages = []

    def balance(self,m):
        fiscHelp = 0.
        fiscCost = 0.
        for adv in self.advantages:
            if m/12. <= adv['years']: fiscHelp += adv['value']/12.
        return fiscHelp - fiscCost

    def addAdvantage(self,value=None,years=None):
        self.advantages.append({'value':value , 'years' : years})
