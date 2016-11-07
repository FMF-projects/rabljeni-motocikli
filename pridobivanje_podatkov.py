import orodja1
import re

#======================================================================================================================
#   Pri iskanju oglasov na mobile.de se prikaže le prvih 50 strani, kar bi pomenilo le dobrih 1000 oglasov.
#   Zato sem iskanje razdelila na kategorije motorjev in letnike prve registracije.
#======================================================================================================================

vsa_leta = ['2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016']
vse_kategorije = ['ChopperAndCruiser', 'EnduroAndTouringEnduro', 'NakedBike',
              'SportsAndSuperSportsBike', 'SportTouringMotorcycle',
              'SuperMoto', 'Tourer']

#======================================================================================================================
#   Najprej za vsako kategorijo in leto prve registracije shranimo prvo stran oglasov. Tako bomo izvedeli na koliko
#   straneh so iskani oglasi.
#======================================================================================================================
vsi_oglasi = {}
for kategorija in vse_kategorije:
    for leto in vsa_leta:
        osnovni_naslov = 'http://suchen.mobile.de/fahrzeuge/search.html'
        parametri1 = 'isSearchRequest=true&scopeId=MB&usage=USED'
        vrsta_motorja = '&categories={}'.format(kategorija)
        letnik_motorja = '&minFirstRegistrationDate={}-01-01&maxFirstRegistrationDate={}-12-31'.format(leto, leto)
        parametri2 = '&maxPowerAsArray=PS&minPowerAsArray=PS&fuels=PETROL&transmissions=MANUAL_GEAR'
        parametri3 = '&minCubicCapacity=500&damageUnrepaired=NO_DAMAGE_UNREPAIRED'

        naslov = '{}?{}{}{}{}{}'.format(osnovni_naslov, parametri1, vrsta_motorja,
                                        letnik_motorja, parametri2, parametri3)
        datoteka = 'stevilo_strani/{}_{}.html'.format(leto, kategorija)
        orodja1.shrani(naslov, datoteka)

        with open(datoteka, encoding="utf8") as f:
            # V izvorni kodi vsake prve strani poiščemo vsa ujemanja s pageNumber in tako dobimo največje število,
            # ki nam pove število vseh strani.
            vsebina = f.read()
            stevila = []
            for prva_stran_oglasov in re.finditer(
                    r'pageNumber=(?P<stevilo_strani>\d{1,2})'
                    , vsebina):

                stevila.append(int(prva_stran_oglasov.group('stevilo_strani')))
            stevilo_strani = (max(stevila))

#======================================================================================================================
#   Sedaj lahko za vsako kategorijo in leto shranimo vse prikazane oglase in tako skupaj dobimo veliko več kot le
#   1000 zadetkov.
#======================================================================================================================

        for stran in range(1, stevilo_strani + 1):
            nov_naslov = naslov + '&pageNumber={}'.format(stran)
            datoteka_1 = 'motocikli/{}_{}_{:02}.html'.format(leto, kategorija, stran)
            orodja1.shrani(nov_naslov, datoteka_1)

#======================================================================================================================
#   V html datotekah bomo za vsak oglas poiskali id, opis in ceno motocikla,

            # with open(datoteka_1, encoding="utf8") as h:
            #     vsebina = h.read()
            #     for oglas in re.finditer(
            #             r'id=(?P<id>\d{9})'
            #             r'.+?<span class="h3 u-text-break-word">(?P<motor>.+?)</span>'
            #             r'.+?<span class="h3 u-block">(?P<cena>.+?)</span>'
            #             r'.+?class="rbt-regMilPow">(?P<opis>.+?)</div>'
            #              , vsebina):
            #
            #         podatki_oglasa = {}
            #         id = int(oglas.group('id'))
            #         podatki_oglasa['motor'] = oglas.group('motor')
            #         podatki_oglasa['cena'] = oglas.group('cena')
            #         podatki_oglasa['opis'] = oglas.group('opis')
            #         vsi_oglasi[id] = podatki_oglasa

#======================================================================================================================
#   Preden podatke shranimo v csv datoteko, jih moramo še urediti.
#======================================================================================================================

