import streamlit as st
import pandas as pd
from hpb_coupon_scraper import scrape_hpb_coupon
import io

st.set_page_config(page_title="HPB Coupon Scraper", layout="wide")

st.title("Hot Pepper Beauty Coupon Scraper")
st.markdown("""
ホットペッパービューティーのサロンURLを入力して、**クーポン情報のみ**を取得します。
- 複数のURLを入力して、店舗間のクーポン比較が可能です。
- 全ページのクーポンを取得します。
- 取得結果はExcelでダウンロードできます。
""")

# Input Area
url_input = st.text_area("対象のURLを入力してください（1行に1つ）", height=150,
                        placeholder="https://beauty.hotpepper.jp/slnH000306271/\nhttps://beauty.hotpepper.jp/slnH000xxxxxx/")

if 'coupon_data' not in st.session_state:
    st.session_state.coupon_data = []

if st.button("クーポン情報を取得"):
    urls = [url.strip() for url in url_input.split('\n') if url.strip()]
    
    if not urls:
        st.warning("URLを入力してください。")
    else:
        all_data = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, url in enumerate(urls):
            status_text.text(f"Processing ({i+1}/{len(urls)}): {url}")
            # Max pages 20 just to be safe, though usually fewer
            data = scrape_hpb_coupon(url, max_pages=20)
            if data:
                all_data.extend(data)
            progress_bar.progress((i + 1) / len(urls))
            
        status_text.text("完了しました！")
        progress_bar.progress(100)
        st.session_state.coupon_data = all_data

if st.session_state.coupon_data:
    all_data = st.session_state.coupon_data
    df = pd.DataFrame(all_data)
    
    # Reorder columns
    cols = ['salon_name', 'eligibility', 'icons', 'name', 'price', 'conditions']
    # Ensure columns exist
    for col in cols:
        if col not in df.columns:
            df[col] = ""
    df = df[cols]
    
    st.success(f"{len(df)} 件のクーポンを取得しました。")
    
    # Display Data
    st.dataframe(df, use_container_width=True)
    
    # Excel Export
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Coupon List')
        
        # Adjust column widths for better readability (optional simple adjustment)
        worksheet = writer.sheets['Coupon List']
        for column in worksheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            # Limit max width
            if adjusted_width > 50:
                adjusted_width = 50
            worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

    st.download_button(
        label="Excelをダウンロード",
        data=buffer.getvalue(),
        file_name="hpb_coupon_list.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
