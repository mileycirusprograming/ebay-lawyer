from bs4 import BeautifulSoup
import requests
import codecs

url = "https://www.ebay.de/itm/Original-Audi-19-Zoll-Felgen-A4-S4-B9-Alufelgen-Sommerreifen-Neu-Sommerrader/173837096716?_trkparms=aid%3D111001%26algo%3DREC.SEED%26ao%3D1%26asc%3D20180816085401%26meid%3Dea18f30fdbb747cab5190f43fe9b28ba%26pid%3D100970%26rk%3D2%26rkt%3D2%26sd%3D290870810757%26itm%3D173837096716&_trksid=p2481888.c100970.m5481&_trkparms=pageci%3Ad401779d-4a6c-11e9-94c6-74dbd180f0d4%7Cparentrq%3A97020f691690ad78ab4a7810fffe176a%7Ciid%3A1"

NOT_FOUND = "/wordnotfound"

def check_blacklist(blacklist_path, text):
    #open file for checking
    file_handler = codecs.open(blacklist_path, 'r', 'iso-8859-15')
    lines = file_handler.read().splitlines()

    #check for every blacklisted word
    for line in lines:
        if text.find(line) > -1:
            #blacklisted word found
            return line
    #no blacklisted word found
    return NOT_FOUND

def check_mandatory(mandatorylist_path, text):
    #open file for checking
    file_handler = codecs.open(mandatorylist_path, 'r', 'iso-8859-15')
    lines = file_handler.read().splitlines()

    #check for every mandatory word
    missing_words = []
    for line in lines:
        if text.find(line) == -1:
            #mandatory word not found
            missing_words.append(line)
    return missing_words



# Downloads the eBay page for processing
res = requests.get(url)
# Raises an exception error if there's an error downloading the website
res.raise_for_status()
# Creates a BeautifulSoup object for HTML parsing
soup = BeautifulSoup(res.text, 'html.parser')
# Scrapes the first listed item's name
#name = soup.find("h3", {"class": "s-item__title"}).get_text(separator=u" ")


rechtl = soup.find("div", {"class": "bsi-aci bsi-aci-addl-pd"}).get_text(separator=u" ")
agb = soup.find("textarea", {"id": "bsiTermsConditions"}).get_text(separator=u" ")
widerrufsb = soup.find("div", {"class": "bsf-rt-pad rpDetails"}).get_text(separator=u" ")

# Scrapes the first listed item's price
#price = soup.find("span", {"class": "s-item__price"}).get_text()

# Prints the url, listed item name, and the price of the item
print(url)
#print("Rechtliche Informationen: " + rechtl)
#print("Agb: " + agb)
#print("Widerrufsbelehrung: " + widerrufsb + "\n")

print (check_blacklist("listen/blacklist_widerspruechliche_Widerrufsfristen.txt", rechtl))
print (check_mandatory("listen/mandatory gesetzliche Mängelhaftung.txt", widerrufsb))

#print (widerrufsb)