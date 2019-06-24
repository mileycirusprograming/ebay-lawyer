from bs4 import BeautifulSoup
import requests
import codecs
import os

PAGES = 3

path_blacklist = os.getcwd() + "/blacklist"
path_mandatory = os.getcwd() + "/mandatory"
path_query = os.getcwd() + "/search_query.txt"

def read_query(path):
    file_handler = codecs.open(path, 'r', 'iso-8859-15')
    lines = file_handler.read().splitlines()
    return lines

def get_files(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            #if '.txt' in file:
            files.append(os.path.join(r, file))
    return files


def check_blacklist(blacklist_path, text):
    #open file for checking
    file_handler = codecs.open(blacklist_path, 'r', 'iso-8859-15')
    lines = file_handler.read().splitlines()

    found_words = []
    #check for every blacklisted word
    for line in lines:
        if text.find(line) > -1:
            #blacklisted word found
            found_words.append(str(line))
    return list(dict.fromkeys(found_words))

def check_mandatory(mandatorylist_path, text):
    #open file for checking
    file_handler = codecs.open(mandatorylist_path, 'r', 'iso-8859-15')
    lines = file_handler.read().splitlines()

    #check for every mandatory word
    for line in lines:
        if text.find(line) > -1:
            #mandatory word found
            return False
    return True

def get_html(url):
    # Downloads the eBay page for processing
    res = requests.get(url)
    # Raises an exception error if there's an error downloading the website
    res.raise_for_status()
    # Creates a BeautifulSoup object for HTML parsing
    soup = BeautifulSoup(res.text, 'html.parser')
    # Scrapes the first listed item's name
    # name = soup.find("h3", {"class": "s-item__title"}).get_text(separator=u" ")
    return soup

def evaluate(url):
    blacklisted = []
    blacklisted_details = []
    mandatory = []
    mandatory_details = []

    soup = get_html(url)
    rechtl = soup.find("div", {"class": "bsi-aci bsi-aci-addl-pd"})#.get_text(separator=u" ")
    agb = soup.find("textarea", {"id": "bsiTermsConditions"})#.get_text(separator=u" ")
    widerrufsb = soup.find("div", {"class": "bsf-rt-pad rpDetails"})#.get_text(separator=u" ")


    texts = [rechtl, agb, widerrufsb]

    for blacklist_path in get_files(path_blacklist):
        for text in texts:
            if text:
                get_text = text.get_text(separator=u" ")
                check = check_blacklist(blacklist_path, get_text)
                if check:
                    blacklisted.append(str(os.path.basename(blacklist_path)))
                    blacklisted_details.extend(check)

    for mandatory_path in get_files(path_mandatory):
        check = True
        for text in texts:
            if text:
                get_text = text.get_text(separator=u" ")
                check = check and check_mandatory(mandatory_path, get_text)

        if check:
            mandatory.append(str(os.path.basename(mandatory_path)))
            mandatory_details.append(str(os.path.basename(mandatory_path)))

    return sorted(dict.fromkeys(blacklisted), reverse=True), sorted(dict.fromkeys(blacklisted_details), reverse=True), sorted(dict.fromkeys(mandatory)), sorted(dict.fromkeys(mandatory_details), reverse=True)

def search(query):
    results = []
    url = "https://www.ebay.de/sch/i.html?_nkw=" + str(query) + "&LH_SellerType=2"
    id_listing = "sresult lvresult clearfix li"
    id_listing_shic = "sresult lvresult clearfix li shic"
    for page_number in range(1, PAGES + 1):
        page_url = url + "&_pgn=" + str(page_number)
        soup = get_html(page_url)
        #iterate through all search results (50 per page)
        for i in range(1,51):
            li1 = soup.find("li", {"class": id_listing, "r": str(i)})
            if not li1:
                li1 = soup.find("li", {"class": id_listing_shic, "r": str(i)})
            if li1:
                href = li1.find("a", {"class": "vip"})["href"]
                results.append(href)
    return results

pages_input = input("Number of pages to search: ")
try:
   pages_int = int(pages_input)
   PAGES = pages_int
except ValueError:
   print(pages_input, "is not a valid number.")
   print("Searching", PAGES, "pages by default.")

search_terms = read_query(path_query)
print()
print("Start search with", len(search_terms), "search terms.", end="\r")
for search_term in search_terms:
    print()
    print()
    print("Search term:", search_term)
    print("Evaluating", PAGES, "pages.")
    search_results = search(search_term)

    file_result = open("search_results/" + search_term + ".txt", "w")
    file_details = open("search_results/details/" + search_term + ".txt", "w")
    for url in search_results:
        print("Processed", search_results.index(url) + 1, "of", len(search_results), "links.", end="\r")
        blacklisted, blacklisted_details, mandatory, mandatory_details = evaluate(url=url)
        #print("blacklisted:", blacklisted)
        #print("mandatory:", mandatory)

        if blacklisted or mandatory:
            file_result.write(" +++ " + url + "\n")
            file_result.write("\n")
            file_result.write("blacklisted:" + str(blacklisted) + "\n")
            file_result.write("\n")
            file_result.write("mandatory:" + str(mandatory) + "\n")
            file_result.write("\n")
            file_result.write("\n")

            file_details.write(" +++ " + url + "\n")
            file_details.write("\n")
            file_details.write("blacklisted:" + str(blacklisted_details) + "\n")
            file_details.write("\n")
            file_details.write("mandatory:" + str(mandatory_details) + "\n")
            file_details.write("\n")
            file_details.write("\n")

print()
print("Search completed.")