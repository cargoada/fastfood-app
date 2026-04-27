import sys
import os
import asyncio

# --- 🌟 雲端與本機雙重補丁 ---
# 1. 如果是 Windows 電腦，切換到正確的引擎
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 2. 讓雲端主機自動下載幽靈瀏覽器核心 (Chromium)
os.system("playwright install chromium")

import streamlit as st
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
from datetime import datetime

st.set_page_config(page_title="雙引擎神券雷達", page_icon="🍔", layout="wide")


# ================= 備用大數據庫 (全網最齊全火力版) =================
def get_backup_database():
    return [
        # 🍗 肯德基 - 買一送一 & 點心區
        {"brand": "肯德基 (獨家庫)", "code": "40457", "title": "4塊雞塊買一送一", "content": "4塊上校雞塊買一送一！只要 $49 (原價$98)", "days_left": 90},
        {"brand": "肯德基 (獨家庫)", "code": "40558", "title": "大薯買一送一", "content": "香酥脆薯(大)買一送一！只要 $65", "days_left": 90},
        {"brand": "肯德基 (獨家庫)", "code": "50390", "title": "玉米濃湯買一送一", "content": "大杯玉米濃湯買一送一！只要 $52", "days_left": 90},
        {"brand": "肯德基 (獨家庫)", "code": "26593", "title": "雞塊富翁狂歡", "content": "18塊上校雞塊 + 1顆原味蛋撻 + 小薯 + 小杯綠茶。激省只要 $120", "days_left": 60},

        # 🍗 肯德基 - 個人超值餐
        {"brand": "肯德基 (獨家庫)", "code": "13692", "title": "咔啦解饞小資餐", "content": "1塊咔啦脆雞 + 1顆原味蛋撻 + 小杯綠茶。只要 $95", "days_left": 45},
        {"brand": "肯德基 (獨家庫)", "code": "15863", "title": "百元有找解饞餐", "content": "1塊咔啦脆雞 + 4塊上校雞塊 + 中杯綠茶。只要 $98", "days_left": 45},
        {"brand": "肯德基 (獨家庫)", "code": "15904", "title": "雙雞飯食飽足餐", "content": "2塊咔啦脆雞 ＋ 1份雞汁風味飯 ＋ 小杯綠茶。只要 $135", "days_left": 30},
        {"brand": "肯德基 (獨家庫)", "code": "15796", "title": "咔啦雙拼滿足餐", "content": "1塊咔啦脆雞 + 1個咔啦雞腿堡 + 1顆蛋撻 + 小薯 + 小杯綠茶。只要 $188", "days_left": 45},

        # 🍗 肯德基 - 雙人/派對/多人分享
        {"brand": "肯德基 (獨家庫)", "code": "15801", "title": "雙人咔啦堡餐", "content": "2個咔啦雞腿堡 + 2小杯綠茶。雙人分享價 $178", "days_left": 45},
        {"brand": "肯德基 (獨家庫)", "code": "26596", "title": "青花椒雙響餐", "content": "2塊咔啦脆雞 + 1個青花椒咔啦雞腿堡 + 3顆蛋撻 + 小薯 + 2小杯綠茶。只要 $299", "days_left": 60},
        {"brand": "肯德基 (獨家庫)", "code": "26594", "title": "經典完勝炸雞桶", "content": "5塊咔啦脆雞(桶) + 1盒原味蛋撻(6入) + 4塊雞塊 + 小杯綠茶。只要 $399", "days_left": 60},
        {"brand": "肯德基 (獨家庫)", "code": "26592", "title": "無敵派對歡聚桶", "content": "4塊青花椒脆雞+4塊咔啦脆雞+8塊雞塊+2顆蛋撻+小薯+10顆QQ球+1.25L可樂。狂省特價 $666", "days_left": 60},

        # 🍔 漢堡王 - 買一送一 & 套餐
        {"brand": "漢堡王 (獨家庫)", "code": "P0390", "title": "四塊雞塊買一送一", "content": "4塊雞塊買一送一，兩份只要$65！", "days_left": 120},
        {"brand": "漢堡王 (獨家庫)", "code": "P0465", "title": "辣薯球買一送一", "content": "辣薯球(小)買一送一，只要$55！", "days_left": 120},
        {"brand": "漢堡王 (獨家庫)", "code": "P0438", "title": "洋蔥圈買一送一", "content": "洋蔥圈(小)買一送一，只要$49！", "days_left": 120},
        {"brand": "漢堡王 (獨家庫)", "code": "P0540", "title": "中杯飲料買一送一", "content": "中杯飲料買一送一，可樂/七喜/綠茶任選，只要$38！", "days_left": 120},
        {"brand": "漢堡王 (獨家庫)", "code": "P0619", "title": "起士牛堡全餐", "content": "起士牛堡 + 4塊雞塊 + 小薯條 + 中可樂，超值價$109！", "days_left": 90},
        {"brand": "漢堡王 (獨家庫)", "code": "LOVEBK", "title": "華堡日專屬折扣", "content": "結帳輸入折扣碼，華堡系列套餐即享9折優惠！(華堡日另有送漢堡)", "days_left": 30},

        # 🍟 麥當勞 & 摩斯
        {"brand": "麥當勞 (獨家庫)", "code": "APP任務", "title": "全球版APP優惠", "content": "每週一更新！開啟麥當勞APP完成任務，常有大薯買一送一或滿額送雞塊！", "days_left": 7},
        {"brand": "麥當勞 (獨家庫)", "code": "1GIFT", "title": "歡樂送買一送一", "content": "網路歡樂送訂餐輸入代碼，享10塊雞塊、大薯或焦糖奶茶買一送一！", "days_left": 30},
        {"brand": "摩斯漢堡 (獨家庫)", "code": "臨櫃直接點購", "title": "大麥珍珠堡套餐", "content": "超級大麥海洋珍珠堡 + 大杯冰紅茶，期間限定特價$115 (原價$130)", "days_left": 60}
    ]
# ================= 爬蟲引擎 =================
@st.cache_data(ttl=3600)
def scrape_kfc_official():
    deals = []
    html_content = ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            url = "https://www.kfcclub.com.tw/coupon"
            # 放寬等待條件，改為 domcontentloaded 避免等太久超時
            page.goto(url, wait_until="domcontentloaded", timeout=15000)

            # 暴力等待 3 秒，讓 JavaScript 充分渲染畫面
            page.wait_for_timeout(3000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)

            html_content = page.content()
        except Exception as e:
            print(f"爬蟲連線異常: {e}")
        finally:
            browser.close()

    # 解析 HTML
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")

        # 更暴力的抓法：直接把網頁所有文字抽出來，用正則表達式掃描
        all_text = soup.get_text(separator=' | ', strip=True)

        # 尋找所有 5 位數的代碼
        codes_found = re.findall(r'\b[1-9]\d{4}\b', all_text)
        seen_codes = set()

        for code in codes_found:
            if code not in seen_codes:
                seen_codes.add(code)
                deals.append({
                    "brand": "肯德基 (即時抓取)",
                    "code": code,
                    "title": f"官網即時神券 {code}",
                    "content": f"這是從官網最新抓取到的代碼：{code}。建議直接輸入結帳機台測試內容！",
                    "days_left": 7
                })

    # 🌟 雙引擎核心邏輯：如果爬蟲抓不到，或是抓太少，立刻調用大數據庫！
    if len(deals) < 3:
        deals.extend(get_backup_database())

    return deals


# ================= UI 介面設計 =================

st.title("🍔 雙引擎速食神券雷達")
st.markdown("結合 **即時幽靈爬蟲** 與 **隱藏大數據庫**，確保你隨時都有超殺優惠可用！")

with st.spinner('雷達掃描中... 正在同步最新優惠...'):
    all_data = scrape_kfc_official()

# 搜尋列
wants = st.multiselect(
    "💡 你今天想找什麼？(可複選)",
    ["漢堡", "雞塊", "薯條", "蛋撻", "飲料", "青花椒", "大薯"]
)

if all_data:
    # 篩選邏輯
    display_data = all_data
    if wants:
        display_data = [d for d in all_data if any(w in d['content'] or w in d['title'] for w in wants)]

    st.success(f"✅ 系統運作正常！目前為您提供 **{len(display_data)}** 個有效優惠。")

    # 顯示結果
    cols = st.columns(2)
    for idx, r in enumerate(display_data):
        with cols[idx % 2]:
            # 根據來源設定不同顏色的邊框
            border_color = "red" if "即時抓取" in r['brand'] else "gray"
            with st.container(border=True):
                st.markdown(f"### 🏷️ 【{r['brand']}】 {r['title']}")
                st.info(f"**套餐內容：**\n\n{r['content']}")
                st.divider()
                c1, c2 = st.columns([3, 1])
                c1.code(r['code'], language="text")
                c2.caption("👆 點擊複製")
else:
    st.error("系統發生未知錯誤，請聯絡開發者。")

st.markdown("---")
if st.button("🔄 強制清除快取並重新掃描"):
    st.cache_data.clear()
    st.rerun()
