import requests
from bs4 import BeautifulSoup
import re
import json
import sys
import time

# Force stdout to use utf-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def clean_text(text):
    if not text:
        return ""
    # User requested to keep brackets for coupons.
    # Just remove extra whitespace.
    return " ".join(text.split())



def extract_salon_name(soup):
    try:
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'BreadcrumbList':
                    items = data.get('itemListElement', [])
                    for item in items:
                        if item.get('position') == 5:
                             return item.get('item', {}).get('name', '')
            except:
                continue
        
        title = soup.title.string if soup.title else ""
        if title:
            return title.split('｜')[0].strip()
            
    except Exception:
        pass
    return "Unknown Salon"

def scrape_hpb_coupon(base_url, max_pages=10):
    # Ensure URL ends with /coupon/
    if not base_url.endswith('/coupon/'):
        if base_url.endswith('/'):
             base_url += 'coupon/'
        else:
             base_url += '/coupon/'

    all_coupons = []
    
    # We will loop through PN1, PN2, ...
    # The first page is often just .../coupon/ but can be treated as page 1.
    # Subsequent pages are .../coupon/PN{i}.html
    
    for page_num in range(1, max_pages + 1):
        if page_num == 1:
            target_url = base_url
        else:
            target_url = f"{base_url}PN{page_num}.html"
            
        print(f"Fetching: {target_url}", file=sys.stderr)
        
        try:
            response = requests.get(target_url)
            response.encoding = response.apparent_encoding
            
            # If page doesn't exist (e.g. 404), we stop
            if response.status_code == 404:
                print("Page not found, stopping pagination.", file=sys.stderr)
                break
            
            if response.status_code != 200:
                print(f"Error: Status code {response.status_code}", file=sys.stderr)
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract info primarily from the first page? Or update per page?
            # Usually salon name is same.
            if page_num == 1:
                salon_name = extract_salon_name(soup)
            
            # Find coupon list block
            # Coupons are usually in div.couponList > ul > li OR just sequential elements
            # Based on user description: td class="couponLabelCT01" suggests a table structure?
            # Actually HPB coupons are often in tables (class="couponListTbl") or divs based on newer designs.
            # User snippet shows: <p class="couponMenuName"> etc.
            # Let's look for the container. Usually "div.couponDetail" or "table.couponListTbl"
            
            # Strategy: Coupons are often in a table structure.
            # Look for all 'tr' that might contain a coupon.
            # Structure: <tr> <td class="couponLabelCT01">...</td> <td class="bgWhite"> ... <p class="couponMenuName">...</td> </tr>
            
            trs = soup.find_all('tr')
            if not trs and page_num == 1:
                # Try finding div structure if table fails, though debug showed table parts
                coupon_blocks = soup.find_all('div', class_='couponDetail')
                # (Previous logic for div blocks could represent fallback, but let's stick to TR for now based on debug)
            
            # If no TRs found, might be odd. But let's proceed.
            
            for tr in trs:
                # Check if this TR is a coupon row
                # Must have couponMenuName or couponLabelCT01
                name_tag = tr.find('p', class_='couponMenuName')
                if not name_tag:
                    continue

                # 1. Eligibility
                eligibility = ""
                # Look for any class starting with couponLabel
                el_tag = tr.find(class_=re.compile(r'couponLabel.*'))
                if el_tag:
                    eligibility = clean_text(el_tag.get_text())
                else:
                    # User wants ALL coupons, but we must exclude "Menu" items that appear on the same page.
                    # Coupons usually ALWAYS have a label (New, All, Step-up, etc.)
                    # If this row has NO label class, it is likely a Standard Menu row. Use continue to skip.
                    continue
                
                # Removed the "continue" skip. We want ALL coupons.
                # The primary check is 'name_tag' existence which identifies it as a menu/coupon row.

                # 2. Menu Icons
                icons = []
                # Search within the TR
                icon_list = tr.find('ul', class_='couponMenuIcons')
                if icon_list:
                    for li in icon_list.find_all('li'):
                        icons.append(clean_text(li.get_text()))
                icons_str = ", ".join(icons)

                # 3. Name
                name = clean_text(name_tag.get_text())

                # 4. Price
                price = ""
                price_tag = tr.find('p', class_='couponMenuPrice')
                if price_tag:
                    price = clean_text(price_tag.get_text())

                # 5. Conditions
                conditions_str = ""
                cond_list = tr.find('dl', class_='couponConditionsList')
                if cond_list:
                    pairs = []
                    dts = cond_list.find_all('dt')
                    dds = cond_list.find_all('dd')
                    
                    if len(dts) == len(dds):
                        for dt, dd in zip(dts, dds):
                             k = clean_text(dt.get_text())
                             v = clean_text(dd.get_text())
                             if not k.endswith('：') and not k.endswith(':'):
                                 k += '：'
                             pairs.append(f"{k} {v}")
                    else:
                        conditions_str = clean_text(cond_list.get_text())
                    
                    if pairs:
                        # Use newline for display/excel
                        conditions_str = "\n".join(pairs)

                all_coupons.append({
                    "salon_name": salon_name,
                    "eligibility": eligibility,
                    "icons": icons_str,
                    "name": name,
                    "price": price,
                    "conditions": conditions_str
                })

            # Pagination Check
            has_next = False
            
            # Method 1: Check for "next" link class
            # Common pattern: <li class="next"><a ...></a></li> or <a ... class="next"></a>
            next_link = soup.select_one('li.next > a') or soup.select_one('a.next') or soup.find(class_='arrowPagingR')
            
            if next_link:
                has_next = True
            
            # Method 2: Check if "paging" exists and we are not at end (heuristic)
            if not has_next:
                # Check for explicit paging list
                paging_ul = soup.find(class_='paging') or soup.find(class_='jscPagingParents')
                if paging_ul:
                    # Check if there is a link for next page number
                    # e.g. current is span, next is a
                    current_span = paging_ul.find('span', class_='current')
                    if current_span:
                        current_page_idx = -1
                        # Find index of current span in children
                        try:
                             # This is brittle. Better to trust the loop:
                             # If we found coupons, and we are not at max_pages, let's try next.
                             # BUT that triggers 404s. 
                             # User showed: <li class="pa top0 right0 afterPage"><a ...><span class="iS arrowPagingR">次の25件</span></a></li>
                             # "afterPage" class seems key.
                             if soup.find(class_='afterPage'):
                                 has_next = True
                        except:
                            pass

            if not has_next:
                 # If we can't find a next link, stop.
                 break

        except Exception as e:
            print(f"Error on page {page_num}: {e}", file=sys.stderr)
            break
            
    return all_coupons

if __name__ == "__main__":
    target_url = "https://beauty.hotpepper.jp/slnH000122973/coupon/"
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    
    data = scrape_hpb_coupon(target_url)
    print(json.dumps(data, ensure_ascii=False, indent=2))
