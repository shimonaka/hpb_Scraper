from bs4 import BeautifulSoup

try:
    with open('temp_page.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    first_table = soup.find('table', class_='menuTbl')
    
    if first_table:
        print(f"Found table.menuTbl. Checking div.pT10 inside td.bgWhite:")
        td = first_table.find('td', class_='bgWhite')
        if td:
             wrapper = td.find('div', class_='pT10')
             if wrapper:
                 for child in wrapper.descendants:
                     if child.name:
                         print(f"    Tag: {child.name}, Class: {child.get('class')}")
                         # print(f"    Text: {child.get_text(strip=True)[:50]}")
    else:
        print("Could not find table.menuTbl")

except Exception as e:
    print(f"Error: {e}")
