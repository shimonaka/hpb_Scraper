import requests

url = 'https://beauty.hotpepper.jp/slnH000306271/coupon/'
try:
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    with open('temp_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("Successfully saved to temp_page.html")
except Exception as e:
    print(f"Error: {e}")
