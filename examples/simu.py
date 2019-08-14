# coding: utf-8
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import loan.loan as loan
import loan.estate as estate
import loan.investment as investment
import loan.fiscality as fiscality
# ============ FOR 2AXIS plot
def make_twinXformat(current,other):
        # current and other are axes
    def format_coord(x,y):
        #x a dn y are data coordinates
        # convert them to display coords
        display_coord = current.transData.transform((x,y))
        inv = other.transData.inverted()
        ax_coord = inv.transform(display_coord)
        return 'X={X} ,Y1={Y1}, Y2={Y2}'.format(X=x,Y1=ax_coord[1],Y2=y)
    return format_coord
# ============

neuf          = True
hasPTZ        = True
hasPrimo      = False
hasPatronal1  = False
hasPatronal2  = False
notaireOffert = True
notaireNeuf   = 2.03
apport        = 24500.
# couts et capitaux empruntes
differe = 1.5
assurance = 13000.
# - PTZ
deffPTZ   = differe
dureePTZ  = 20 - deffPTZ
# - Principal
tauxP     = 1.65
deffP     = differe
dureeP    = 25 + deffP
# - Primo
deffPrimo = differe
Primo     = 30000.
# - Patronal
Patronal1     = 25000
tauxPatronal1 = 0.0
deffPatronal1 = differe
dureePatronal1= 20

Patronal2     = 25000
tauxPatronal2 = 1.0
deffPatronal2 = differe
dureePatronal2= 20

price   = 382000.+10000.
travaux = 0000.
#price = 382000.
decaissements = []
decaissements.append({'name':'Reservation'  , 'rate' : 5 , 'termM' : 0  })
decaissements.append({'name':'Signature'    , 'rate' :15 , 'termM' : 0  })
decaissements.append({'name':'Fondations'   , 'rate' :15 , 'termM' : 3  })
decaissements.append({'name':'RDC'          , 'rate' :15 , 'termM' : 6  })
decaissements.append({'name':'2e etage'     , 'rate' :10 , 'termM' : 9  })
decaissements.append({'name':'Hors eau'     , 'rate' :10 , 'termM' : 12 })
decaissements.append({'name':'Cloisonnement', 'rate' :20 , 'termM' : 15 })
decaissements.append({'name':'Achevement'   , 'rate' : 5 , 'termM' : 16 })
decaissements.append({'name':'Reception'    , 'rate' : 5 , 'termM' : 18 })
# = decaissements = []
# = decaissements.append({'name':'Reservation'      , 'rate' : 2 , 'termM' : 0  })
# = decaissements.append({'name':'Debut trav'       , 'rate' :23 , 'termM' : 2  })
# = decaissements.append({'name':'Debut fondations' , 'rate' : 5 , 'termM' : 3  })
# = decaissements.append({'name':'Fin fondations'   , 'rate' : 5 , 'termM' : 6  })
# = decaissements.append({'name':'Elevation murs'   , 'rate' :30 , 'termM' : 12 })
# = decaissements.append({'name':'Hors eau'         , 'rate' : 5 , 'termM' : 15 })
# = decaissements.append({'name':'Hors air'         , 'rate' :20 , 'termM' : 20 })
# = decaissements.append({'name':'Achevement'       , 'rate' : 5 , 'termM' : 23 })
# = decaissements.append({'name':'Reception'        , 'rate' : 5 , 'termM' : 24 })
# le bien en lui meme
bien = estate.Estate(acqGrossCost   = price,\
                      realtorRate  = (0.0 if neuf else 7.5)   ,\
                      notaryRate   = (0. if notaireOffert else notaireNeuf) if neuf else 7.2   ,\
                      sellRate     = 1.0   ,\
                      rent         = 1100  ,\
                      propertyTax  = 1250  ,\
                      localTax     = 1200  ,\
                      condoFees    = 2100  ,\
                      disbursments = decaissements,\
                      delivery     = deffP,\
                      construction = travaux
        )
print('\n'.join(['{name:<20}: {pmt:>15.2f} au mois numero {term:>3d}'.format(name=dec['name'],pmt=dec['pmt'],term=dec['termM']) for dec in bien.disbursments]))
#for price in priceRange:
PTZ      = 0.4*min(210000.,bien.acqRealtorCost) if hasPTZ else 0.
fisc = fiscality.Fiscality()
# ========= creation et calcul du projet
projet = investment.Investment(contribution  = apport)
projet.addProperty(bien)
# pret taux zero CA
if hasPrimo :
    projet.addLoan(loan.Loan(termY=dureeP,nominalRate=0,principal=Primo,name='Primo',deffY=deffPrimo,computeNow=False))
# PTZ
if hasPTZ :
    projet.addLoan(loan.Loan(termY=dureePTZ,nominalRate=0,principal=PTZ,name='PTZ',deffY=deffPTZ,computeNow=False))
# Patronal
if hasPatronal1 :
    projet.addLoan(loan.Loan(termY=dureePatronal1,nominalRate=tauxPatronal1,principal=Patronal1,name='Patronal1',deffY=deffPatronal1,computeNow=False))
if hasPatronal2 :
    projet.addLoan(loan.Loan(termY=dureePatronal2,nominalRate=tauxPatronal2,principal=Patronal2,name='Patronal2',deffY=deffPatronal2,computeNow=False))
# pret principal pour le reste
projet.addLoan(loan.Loan(termY=dureeP,nominalRate=tauxP,principal=projet.costLeft,insurance=assurance,name='Principal',deffY=deffP,computeNow=False))
# bilan fiscal
projet.addFiscality(fisc)
# calcul du projet
projet.compute()
yearP = [i for i in range(1,300) if projet.balance(i)>0][0]/12.
# ===    print('==================')
# ===    print('Capital total    : {capTot: 9.2f}'.format(   capTot=projet.funds          ) )
# ===    print('Mensualite pret  : {mensTot: 9.2f}'.format(  mensTot=projet.PMT(1)        ) )
# ===    print('Mensualite ass   : {mensTot: 9.2f}'.format(  mensTot=projet.insFees(1)    ) )
# ===    print('Mensualite totale: {mensTot: 9.2f}'.format(  mensTot=projet.totPMT(1)     ) )
# ===    print('Prix brut        : {prixBrut:9.2f}'.format( prixBrut=projet.acqGrossCost ) )
# ===    print('Annee rentable   : {prixBrut:9.2f}'.format( prixBrut=yearP               ) )
# ===    listYearP.append(yearP)
# ===    listMensTot.append(projet.totPMT(1))
#for l in projet.loans:
#    print('===== ' + l.name)
#    print('capital         : {cap: 9.2f} eur'.format(cap= l.principal))
#    #print('mensualite pret : {mens:9.2f} eur'.format(mens=l.getPMT(1)))
#    #print('rbt princ  pret : {mens:9.2f} eur'.format(mens=l.getPPMT(1)))
#    #print('interet    pret : {mens:9.2f} eur'.format(mens=l.getIPMT(1)))
#    #print('mensualite ass  : {mens:9.2f} eur'.format(mens=l.getInsFees(1)))
#    #print('mensualite tot  : {mens:9.2f} eur'.format(mens=l.getTotPMT(1)))
#    for i in range(l.termM+1):
#        m   = i
#        print('Month {m:03d} , mens: {mens:9.2f} , capital : {cap:9.2f}, interets : {int:9.2f} ,assurance : {ass:9.2f} , total : {menstot:9.2f}'.format(\
#                    m=m,mens=l.getPMT(m),cap=l.getPPMT(m),int=l.getIPMT(m),ass=l.getInsFees(m),menstot=l.getTotPMT(m)))
#for i in range(projet.termM()+1):
#    m   = i
#    print('Mois {m:03d}, mensualite : {mens:9.2f},  capital restant : {cap:9.2f}, interets payes : {int:9.2f} ,prix revente : {rev:9.2f}, balance : {bal:9.2f}'.format(cap=projet.leftCap(m),rev=projet.sellPrice(m),bal=projet.balance(m),int=projet.IPMT(m),mens=projet.PMT(m),m=m))

t = range(projet.termM()+1)
year = lambda m: 2018+(6+m)/12.
pretChaton           = [ 175  if year(m)<2021+ 7/12. else 0. for m in t ]
pretAT               = [ 100. if year(m)<2019+11/12. else 0. for m in t ]
pretChat             = [ 165  if year(m)<2019+ 6/12. else 0. for m in t ]
#pretVoiture          = [ 250  if year(m)<2023+11/12. else 0. for m in t ]
pretVoiture          = [ 50  if year(m)<2048 else 0. for m in t ]
loyer                = [ 1200 if   m<=deffP*12   else 0. for m in t ]
chargeForEndettement = [ projet.totPMT(m) +pretChat[m] +pretChaton[m] +loyer[m] +pretVoiture[m] for m in t]
#for m in t:
#    print(str(m) \
#+ ' '+str(pretChaton           [m])\
#+ ' '+str(pretAT               [m])\
#+ ' '+str(pretChat             [m])\
#+ ' '+str(loyer                [m])\
#+ ' '+str(chargeForEndettement [m])\
#)
if len(t)>1:
    data1    = [ projet.totPMT(m)                                                                     for m in t]
    data1bis = [ projet.monthlyCost(m)                                                                for m in t]
    data1ter = [ projet.monthlyCost(m) + pretVoiture[m] + pretChaton[m] +pretChat[m] +loyer[m]+pretAT[m] for m in t]
    data1ref = [ 86.+250. + pretChaton[m] +pretChat[m] +loyer[0]+pretAT[m] for m in t]
    data2 = [ projet.IPMT(m) for m in t]
    data2 = [ charge/(((2333+2090)*13+1300)/12.)*100. for charge in chargeForEndettement]
    fig , ax1 = plt.subplots()
    color = 'tab:red'
    spacing = 50
    minorLocator = MultipleLocator(spacing)
    spacing = 100
    majorLocator = MultipleLocator(spacing)
    ax1.yaxis.set_minor_locator(minorLocator)
    ax1.yaxis.set_major_locator(majorLocator)
    ax1.set_xlabel('Mois')
    ax1.set_ylabel(u'Mensualité (€)', color=color)
    plt1    =ax1.plot(t, data1   , color=color ,linestyle='-.',label='Paiements pret (ass. incl.)')
    plt1bis =ax1.plot(t, data1bis, color=color ,linestyle='--',label='Pret + charges logement (TF,copro)')
    plt1ter =ax1.plot(t, data1ter, color=color ,linestyle='-' ,label='Pret,charges logement et autres charges')
    plt1ter =ax1.plot(t, data1ref, color='tab:gray' ,linestyle='-' ,label='Charges completes actuelles')
    ax1.grid(color=color, linestyle='-', linewidth=0.2,which='major')
    #ax1.grid(color=color, linestyle='--', linewidth=0.2,which='minor')
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylim([0,100])
    
    color = 'tab:blue'
    ax2.set_ylabel(u'Endettement (%)', color=color)  # we already handled the x-label with ax1
    plt2 = ax2.plot(t, data2, color=color, label='Endettement')
    #ax2.grid(color=color, linestyle='-', linewidth=.2)
    ax2.tick_params(axis='y', labelcolor=color)
    
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    ax1.legend(loc=0)
    ax2.legend(loc=1)
    #plt.title('Bien neuf (avec PTZ)' if neuf else 'Bien ancien')
    ax2.format_coord = make_twinXformat(ax2,ax1)
    plt.show()
