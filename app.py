import streamlit as st
import pandas as pd
from hpb_menu_scraper import scrape_hpb_menu
import io

st.set_page_config(page_title="HPB Menu Scraper", layout="wide")

st.title("Hot Pepper Beauty Menu Scraper")
st.markdown("""
ホットペッパービューティーのサロンURLを入力して、メニュー情報を取得します。
- 複数のURLを入力して、店舗間のメニュー比較が可能です。
- 取得結果はExcelでダウンロードできます。
""")

# Input Area
url_input = st.text_area("対象のURLを入力してください（1行に1つ）", height=150,
                        placeholder="https://beauty.hotpepper.jp/slnH000306271/\nhttps://beauty.hotpepper.jp/slnH000xxxxxx/")

if 'all_data' not in st.session_state:
    st.session_state.all_data = []

if st.button("メニュー情報を取得"):
    urls = [url.strip() for url in url_input.split('\n') if url.strip()]
    
    if not urls:
        st.warning("URLを入力してください。")
    else:
        all_data = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, url in enumerate(urls):
            status_text.text(f"Processing ({i+1}/{len(urls)}): {url}")
            data = scrape_hpb_menu(url)
            if data:
                all_data.extend(data)
            progress_bar.progress((i + 1) / len(urls))
            
        status_text.text("完了しました！")
        progress_bar.progress(100)
        st.session_state.all_data = all_data

if st.session_state.all_data:
    all_data = st.session_state.all_data
    df = pd.DataFrame(all_data)
    
    # Reorder columns
    cols = ['salon_name', 'category', 'name', 'price', 'description']
    # Ensure columns exist even if data is empty or missing keys
    for col in cols:
        if col not in df.columns:
            df[col] = ""
    df = df[cols]
    
    st.success(f"{len(df)} 件のメニューを取得しました。")
    
    # Display Data
    st.dataframe(df, use_container_width=True)
    
    # Excel Export
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Menu List')
    
    st.download_button(
        label="Excelをダウンロード",
        data=buffer.getvalue(),
        file_name="hpb_menu_list.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.write("---")
    st.subheader("WordPress CSV出力設定")
    
    # WP Export Section
    if 'all_data' in locals() and all_data:
        # Identify unique salons
        unique_salons = sorted(list(set(d['salon_name'] for d in all_data)))
        
        st.write("各店舗のカスタム投稿タイプ（スラッグ）を入力してください。")
        cpt_mapping = {}
        
        # Create 2 columns for better layout
        for salon in unique_salons:
            # Provide a default guess if possible, or empty
            default_slug = ""
            cpt_mapping[salon] = st.text_input(f"{salon}", value=default_slug, key=f"cpt_{salon}", placeholder="例: zeal-menu_list")

        if st.button("WP用CSVを作成"):
            from wp_export import convert_to_wp_csv
            
            wp_df = convert_to_wp_csv(all_data, cpt_mapping)
            
            # Convert to CSV
            csv_buffer = wp_df.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="WP用CSVをダウンロード",
                data=csv_buffer,
                file_name="wp_menu_import.csv",
                mime="text/csv"
            )
