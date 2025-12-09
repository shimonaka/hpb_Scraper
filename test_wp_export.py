from wp_export import clean_price_and_get_metadata, convert_to_wp_csv
import pandas as pd
import unittest

class TestWPExport(unittest.TestCase):
    
    def test_clean_price(self):
        # Case 1: Standard price
        p, f = clean_price_and_get_metadata("¥5,500")
        self.assertEqual(p, "5500")
        self.assertEqual(f, "no")
        
        # Case 2: Fluctuation
        p, f = clean_price_and_get_metadata("¥11,000～")
        self.assertEqual(p, "11000")
        self.assertEqual(f, "yes")
        
        # Case 3: Inquiry required
        p, f = clean_price_and_get_metadata("要問い合わせ")
        self.assertEqual(p, "")
        self.assertEqual(f, "no") # Should be whatever default, user said empty value

    def test_csv_conversion(self):
        data = [
            {
                "salon_name": "Salon A",
                "category": "セットメニュー",
                "name": "Menu 1",
                "price": "¥10,000",
                "description": "Desc 1"
            },
             {
                "salon_name": "Salon B",
                "category": "not_exist",
                "name": "Menu 2",
                "price": "要問い合わせ",
                "description": "Desc 2"
            }
        ]
        
        mapping = {
            "Salon A": "cpt_a",
            "Salon B": "cpt_b"
        }
        
        df = convert_to_wp_csv(data, mapping)
        
        # Check rows
        self.assertEqual(len(df), 2)
        
        # Check Row 1
        row1 = df.iloc[0]
        self.assertEqual(row1['post_type'], "cpt_a")
        self.assertEqual(row1['tax_menu_cat'], "setmenu")
        self.assertEqual(row1['menu_price'], "10000")
        self.assertEqual(row1['menu_fluctuation'], "no")
        
        # Check Row 2
        row2 = df.iloc[1]
        self.assertEqual(row2['post_type'], "cpt_b")
        self.assertEqual(row2['tax_menu_cat'], "") # Not in map
        self.assertEqual(row2['menu_price'], "")
        
        
if __name__ == '__main__':
    unittest.main()
