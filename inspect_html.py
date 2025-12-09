from bs4 import BeautifulSoup
import sys

with open('debug_coupon.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Search for couponMenuName
target = soup.find(class_='couponMenuName')
if target:
    print("Found couponMenuName!")
    # Print the parent container (likely 3-4 levels up)
    parent = target.find_parent('div', class_='couponDetail')
    if parent:
        print("Found parent div.couponDetail")
        print(parent.prettify()[:2000]) # Print first 2000 chars
    else:
        print("No div.couponDetail parent. Printing close parent:")
        print(target.parent.parent.prettify()[:2000])

else:
    print("couponMenuName not found.")
    # Print all classes
    # print([c for c in soup.find_all(class_=True)])
