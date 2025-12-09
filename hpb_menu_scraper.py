import requests
from bs4 import BeautifulSoup
import re
import json
import sys

# Force stdout to use utf-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def clean_text(text):
    if not text:
        return ""
    # Remove braces and their content: [], 【】, mixed pairs allowed
    # Matches starting with [ or 【, ending with ] or 】, non-greedy
    cleaned = re.sub(r'[\[【].*?[\]】]', '', text, flags=re.DOTALL)
    # Remove extra whitespace
    return " ".join(cleaned.split())

def extract_salon_name(soup):
    try:
        # Try finding JSON-LD with salon name
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'BreadcrumbList':
                    # Usually the last item or specific position has the salon name
                    # Position 5 in the observed data was the salon name
                    items = data.get('itemListElement', [])
                    for item in items:
                         # Heuristic: the item before "Coupon/Menu" or checking structure
                         if item.get('position') == 5: # Based on observed structure
                             return item.get('item', {}).get('name', '')
            except:
                continue
        
        # Fallback to Title tag
        title = soup.title.string if soup.title else ""
        if title:
            # Common format: "Salon Name｜..."
            return title.split('｜')[0].strip()
            
    except Exception:
        pass
    return "Unknown Salon"

def scrape_hpb_menu(url):
    # URL Validation and Modification
    if not url.endswith('/coupon/'):
        if url.endswith('/'):
            url += 'coupon/'
        else:
            url += '/coupon/'
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
            "Referer": "https://beauty.hotpepper.jp/",
            "Upgrade-Insecure-Requests": "1"
        }
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        if response.status_code != 200:
            print(f"Error: Failed to fetch page. Status code: {response.status_code}", file=sys.stderr)
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract Salon Name
        salon_name = extract_salon_name(soup)
        
        menu_list_title = soup.find(id='menuList')

        if not menu_list_title:
            print("Error: Could not find #menuList element.", file=sys.stderr)
            return []

        menu_data = []
        current_category = "セットメニュー"
        
        # Traverse siblings of #menuList
        sibling = menu_list_title.find_next_sibling()
        while sibling:
            classes = sibling.get('class', [])
            
            # Check for Category Header
            if 'singleMenuHead' in classes:
                # Extract category name
                # Usually in p.b.fl inside the div
                cat_p = sibling.find('p', class_='b')
                if cat_p:
                    current_category = clean_text(cat_p.get_text(strip=True))
            
            # Check for Menu Item Table Container
            # The structure observed: div > table.menuTbl
            elif sibling.name == 'div':
                tables = sibling.find_all('table', class_='menuTbl')
                for table in tables:
                    # Iterate items in the table
                    for tr in table.find_all('tr'):
                        td = tr.find('td', class_='bgWhite')
                        if td:
                            # Extract details
                            name_tag = td.find('p', class_='couponMenuName')
                            price_tag = td.find('p', class_='taR') # price is usually here
                            desc_tag = td.find('p', class_='wbba') # description usually here

                            # Name
                            name = clean_text(name_tag.get_text(strip=True)) if name_tag else ""
                            
                            # Price
                            price = ""
                            if price_tag:
                                # Sometimes price tag has children, we just want text
                                price = clean_text(price_tag.get_text(strip=True))

                            # Description
                            description = clean_text(desc_tag.get_text(strip=True)) if desc_tag else ""

                            if name: # Only add if name exists
                                menu_data.append({
                                    "salon_name": salon_name,
                                    "category": current_category,
                                    "name": name,
                                    "price": price,
                                    "description": description
                                })
            
            sibling = sibling.find_next_sibling()

        return menu_data

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    # Default URL if not provided (for testing/demo)
    target_url = "https://beauty.hotpepper.jp/slnH000306271/coupon/"
    
    # Allow command line argument
    if len(sys.argv) > 1:
        target_url = sys.argv[1]

    result = scrape_hpb_menu(target_url)
    
    # Output JSON to stdout
    print(json.dumps(result, ensure_ascii=False, indent=2))
