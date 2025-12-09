import requests
url = 'https://beauty.hotpepper.jp/slnH000122973/coupon/'
resp = requests.get(url)
resp.encoding = resp.apparent_encoding
with open('debug_coupon.html', 'w', encoding='utf-8') as f:
    f.write(resp.text)
print("Saved debug_coupon.html")
