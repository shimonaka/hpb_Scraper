import pandas as pd
import re

def clean_price_and_get_metadata(price_str):
    """
    Parses the price string to extract the raw number and fluctuation status.
    
    Args:
        price_str (str): The raw price string (e.g., "¥5,500", "¥11,000～", "要問い合わせ").
        
    Returns:
        tuple: (cleaned_price, menu_fluctuation)
            - cleaned_price (str): Numeric string or empty.
            - menu_fluctuation (str): 'yes' or 'no'.
    """
    if not price_str:
        return "", "no"
    
    fluctuation = "no"
    
    # Check for fluctuation indicator
    if "～" in price_str or "~" in price_str:
        fluctuation = "yes"
    
    # Check for "inquiry required"
    if "要問い合わせ" in price_str:
        return "", fluctuation # Requirements say empty if inquiry required
    
    # Remove non-numeric characters except for digits
    # Using regex to remove everything that is NOT a digit
    cleaned_price = re.sub(r'[^\d]', '', price_str)
    
    return cleaned_price, fluctuation

def convert_to_wp_csv(scraped_data, cpt_mapping):
    """
    Converts scraped list of dicts to a pandas DataFrame suitable for WP CSV import.
    
    Args:
        scraped_data (list): List of dicts with keys 'salon_name', 'category', 'name', 'price', 'description'.
        cpt_mapping (dict): Mapping of salon_name -> post_type_slug.
        
    Returns:
        pd.DataFrame: DataFrame formatted for CSV export.
    """
    
    if not scraped_data:
        return pd.DataFrame()

    # Category Slug Mapping
    category_map = {
      'セットメニュー': 'setmenu',
      'カット': 'cut',
      'カラー': 'color',
      'パーマ': 'perm',
      '縮毛矯正': 'straight',
      '髪質改善': 'improvement',
      'トリートメント': 'treatment',
      'ヘッドスパ': 'spa',
      'その他メニュー': 'other',
      '着付け': 'kitsuke',
    }
    
    rows = []
    
    for item in scraped_data:
        salon_name = item.get('salon_name', '')
        
        # Get CPT from mapping, default to empty if not found (though UI should enforce)
        post_type = cpt_mapping.get(salon_name, '')
        
        # Clean Price
        raw_price = item.get('price', '')
        menu_price, menu_fluctuation = clean_price_and_get_metadata(raw_price)
        
        # Map Category
        cat_name = item.get('category', '')
        cat_slug = category_map.get(cat_name, '')
        
        row = {
            'post_type': post_type,
            'post_title': item.get('name', ''),
            'post_content': '', # Description goes to menu_remarks
            'post_status': 'publish',
            'tax_menu_cat': cat_slug, # Using slug for import
            'menu_name': item.get('name', ''), # Custom field 'menu_name'
            'menu_info': '', # Not scraped, empty
            'menu_price': menu_price,
            'menu_fluctuation': menu_fluctuation,
            'menu_price_max': '', # Not scraped
            'menu_plus': 'no', # Default
            'menu_remarks': item.get('description', ''),
            'salon_name_ref': salon_name # Helper column for user reference
        }
        rows.append(row)
        
    df = pd.DataFrame(rows)
    
    # Reorder columns to be nice
    desired_order = [
        'post_type', 'post_title', 'post_content', 'post_status', 'tax_menu_cat',
        'menu_name', 'menu_info', 'menu_price', 'menu_fluctuation', 'menu_price_max', 'menu_plus', 'menu_remarks',
        'salon_name_ref'
    ]
    
    # Filter only columns that exist
    final_cols = [c for c in desired_order if c in df.columns]
    df = df[final_cols]
    
    return df
