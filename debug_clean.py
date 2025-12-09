from hpb_menu_scraper import scrape_hpb_menu
import re

def clean_text(text):
    if not text:
        return ""
    # Remove braces and their content: [], 【】
    # Debug print
    print(f"Original: {repr(text)}")
    cleaned = re.sub(r'\[.*?\]', '', text, flags=re.DOTALL)
    cleaned = re.sub(r'【.*?】', '', cleaned, flags=re.DOTALL)
    print(f"After regex: {repr(cleaned)}")
    return " ".join(cleaned.split())

def debug():
    url = "https://beauty.hotpepper.jp/slnH000306271/coupon/"
    data = scrape_hpb_menu(url)
    if len(data) > 3:
        item = data[3] # Item 3 was the one failing
        print("--- Item 3 Raw Description (from scraper logic, before cleaning) ---")
        # I need to fetch raw text again because scrape_hpb_menu already cleans it.
        # But wait, scrape_hpb_menu USES clean_text.
        # So I can't debug the INPUT to clean_text using the OUTPUT of scrape_hpb_menu.
        # I have to re-implement the scraping part slightly or just modify scrape_hpb_menu to print raw.
        pass

    # Inspect HTML of Item 3
    import requests
    from bs4 import BeautifulSoup
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Locate Item 3
    # Traverse to find the 3rd item
    count = 0
    menu_list = soup.find(id='menuList')
    sibling = menu_list.find_next_sibling()
    while sibling:
        if sibling.name == 'div' and sibling.find('table', class_='menuTbl'):
            table = sibling.find('table', class_='menuTbl')
            for tr in table.find_all('tr'):
                if count == 3:
                     td = tr.find('td', class_='bgWhite')
                     desc_tag = td.find('p', class_='wbba')
                     print(f"--- Item 3 HTML ---")
                     print(desc_tag.prettify())
                     print(f"--- Item 3 Text ---")
                     print(repr(desc_tag.get_text()))
                     return
                count += 1
        sibling = sibling.find_next_sibling()

if __name__ == "__main__":
    debug()
