from hpb_menu_scraper import scrape_hpb_menu
import json

def verify():
    # Test 1: Full URL
    url_full = "https://beauty.hotpepper.jp/slnH000306271/coupon/"
    print(f"Testing {url_full}...")
    data = scrape_hpb_menu(url_full)
    print(f"Items found: {len(data)}")
    if data:
        print("First item:")
        print(json.dumps(data[0], ensure_ascii=False, indent=2))
        
        # Check for categories
        categories = set(d['category'] for d in data)
        print(f"Categories found: {categories}")
        
        from collections import Counter
        cat_counts = Counter(d['category'] for d in data)
        print("Item counts per category:")
        for cat, count in cat_counts.items():
            print(f"  {cat}: {count}")
        
        # Check cleaning
        for i, item in enumerate(data):
            if '[' in item['name'] or '【' in item['name']:
                print(f"WARNING: Bracket found in name (Item {i}): {repr(item['name'])}")
            if '[' in item['description'] or '【' in item['description']:
                print(f"WARNING: Bracket found in description (Item {i}): {repr(item['description'])}")

    # Test 2: Base URL logic
    url_base = "https://beauty.hotpepper.jp/slnH000306271/"
    print(f"\nTesting {url_base} (should auto-append coupon/)...")
    data_base = scrape_hpb_menu(url_base)
    print(f"Items found: {len(data_base)}")
    if len(data) == len(data_base):
        print("PASS: URL modification logic seems correct.")
    else:
        print("FAIL: Item count mismatch.")

if __name__ == "__main__":
    verify()
