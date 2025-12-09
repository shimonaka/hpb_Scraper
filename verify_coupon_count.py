from hpb_coupon_scraper import scrape_hpb_coupon
import json

url = "https://beauty.hotpepper.jp/slnH000122973/coupon/"
print(f"Scraping {url}...")
data = scrape_hpb_coupon(url)
print(f"Total coupons found: {len(data)}")

# Print first 3 and last 3 names to verify range
if data:
    print("First 3:")
    for d in data[:3]:
        print(f"- [{d['eligibility']}] {d['name']} ({d['price']})")
    print("...")
    print("Last 3:")
    for d in data[-3:]:
        print(f"- [{d['eligibility']}] {d['name']} ({d['price']})")
