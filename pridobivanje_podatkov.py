import orodja1
import re
import unicodedata

#======================================================================================================================
#   Pri iskanju oglasov na mobile.de se prikaže le prvih 50 strani, kar bi pomenilo le dobrih 1000 oglasov.
#   Zato sem iskanje razdelila na kategorije motorjev in letnike prve registracije.
#======================================================================================================================

vsa_leta = ['2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016']
vse_kategorije = ['ChopperAndCruiser','EnduroAndTouringEnduro', 'NakedBike',
              'SportsAndSuperSportsBike', 'SportTouringMotorcycle',
              'SuperMoto', 'Tourer']

#======================================================================================================================
#   Najprej za vsako kategorijo in leto prve registracije shranimo prvo stran oglasov. Tako bomo izvedeli na koliko
#   straneh so iskani oglasi.
#======================================================================================================================
vsi_oglasi = []
for kategorija in vse_kategorije:
    for leto in vsa_leta:
        osnovni_naslov = 'http://suchen.mobile.de/fahrzeuge/search.html'
        parametri1 = 'isSearchRequest=true&scopeId=MB&usage=USED'
        vrsta_motorja = '&categories={}'.format(kategorija)
        letnik_motorja = '&minFirstRegistrationDate={}-01-01&maxFirstRegistrationDate={}-12-31'.format(leto, leto)
        parametri2 = '&maxPowerAsArray=PS&minPowerAsArray=PS&fuels=PETROL&transmissions=MANUAL_GEAR'
        parametri3 = '&minCubicCapacity=500&damageUnrepaired=NO_DAMAGE_UNREPAIRED&maxPrice=30000&minMileage=1000'

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
#   V html datotekah bomo za vsak oglas poiskali id oglasa, znamko, starost, moč, prostornino, ceno in prevožene
#   kilometre motocikla ter jih sočasno še uredili, ter shranili v seznam slovarjev.
#======================================================================================================================

            with open(datoteka_1, encoding="utf8") as h:
                vsebina = h.read()
                for oglas in re.finditer(
                        r'id=(?P<id>\d{9})'
                        r'.+?<span class="h3 u-text-break-word">(?P<motor>.+?)</span>'
                        r'.+?<span class="h3 u-block">(?P<cena>.+?)</span>'
                        r'.+?class="rbt-regMilPow">(?P<opis>.+?)</div>'
                         , vsebina):

                    id = oglas.group('id')

                    motor = oglas.group('motor')
                    motor = motor.split(" ")
                    if motor[0] == 'Moto' or motor[0] == 'MV':
                        znamka = motor[0] + ' ' + motor[1]
                    else:
                        znamka = motor[0]

                    cena = oglas.group('cena')
                    cena = cena.strip('€')
                    cena = cena.strip(' ')
                    cena = int(cena.replace(".",""))

                    opis = oglas.group('opis')
                    opis = opis.encode('ascii', 'replace')
                    opis = opis.decode("utf-8")
                    opis = opis.replace("?", " ")
                    stevilo_vejic = opis.count(',')
                    if stevilo_vejic != 3:
                        continue
                    [letnik, km, moc, prostornina] = opis.split(",")

                    km = km.strip('km')
                    km = km.strip(" ")
                    km = int(km.replace(".", ""))
                    if km > 150000:
                        continue

                    prostornina = prostornina.split()
                    prostornina = prostornina[0]
                    prostornina = int(prostornina.replace(".", ""))
                    if prostornina > 2000:
                        continue

                    letnik = letnik.split("/")
                    letnik = int(letnik[1])

                    moc = moc.split(" ")
                    moc = int(moc[1])
                    if moc > 200:
                        continue

                    tip = kategorija
                    tip = re.findall('[A-Z][a-z]*', tip)
                    tip = ' '.join(tip)

                    podatki_oglasa = {}
                    podatki_oglasa['id'] = id
                    podatki_oglasa['znamka'] = znamka
                    podatki_oglasa['cena'] = cena
                    podatki_oglasa['km'] = km
                    podatki_oglasa['moc'] = moc
                    podatki_oglasa['letnik'] = letnik
                    podatki_oglasa['prostornina'] = prostornina
                    podatki_oglasa['tip'] = tip
                    vsi_oglasi.append(podatki_oglasa)

orodja1.zapisi_tabelo(vsi_oglasi,['id', 'letnik', 'znamka', 'tip', 'prostornina',
                                  'moc', 'km', 'cena'], 'motocikli.csv')