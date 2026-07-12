import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

st.set_page_config(page_title="全網速食神券動態雷達", page_icon="🍔", layout="wide")

# ================= 1. PTT 速食板即時情報 =================
@st.cache_data(ttl=1800)  # 快取 30 分鐘，避免頻繁請求被封鎖
def get_realtime_deals():
    url = "https://www.ptt.cc/bbs/fastfood/index.html"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    realtime_deals = []
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.find_all("div", class_="r-ent")
        
        for article in articles:
            title_tag = article.find("div", class_="title").find("a")
            if not title_tag:
                continue
            title = title_tag.text
            link = "https://www.ptt.cc" + title_tag["href"]
            
            if any(k in title for k in ["情報", "優惠", "買一送一", "代碼"]):
                brand = "綜合/其他"
                if any(k in title for k in ["麥當勞", "麥大", "金拱門"]): brand = "麥當勞"
                elif any(k in title for k in ["肯德基", "KFC", "爺爺"]): brand = "肯德基"
                elif any(k in title for k in ["漢堡王", "華堡", "BK"]): brand = "漢堡王"
                elif "摩斯" in title: brand = "摩斯漢堡"
                elif "拿坡里" in title: brand = "拿坡里"
                elif "必勝客" in title: brand = "必勝客"

                realtime_deals.append({
                    "brand": brand,
                    "code": "詳見內文",
                    "title": f"🔥 PTT情報：{title}",
                    "content": f"網友熱門分享！\n\n👉 **[點擊前往 PTT 原文看詳細討論與代碼]({link})**",
                    "days_left": 7,
                    "source": "PTT即時"
                })
    except Exception as e:
        print(f"PTT 爬蟲異常: {e}")
    return realtime_deals

# ================= 2. Dcard 省錢板即時情報 =================
@st.cache_data(ttl=1800)
def get_dcard_deals():
    url = "https://www.dcard.tw/service/api/v2/forums/savemoney/posts?limit=30"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    dcard_deals = []
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            posts = resp.json()
            for post in posts:
                title = post.get("title", "")
                excerpt = post.get("excerpt", "")
                post_id = post.get("id")
                
                fastfood_keywords = ["麥當勞", "肯德基", "漢堡王", "摩斯", "拿坡里", "必勝客", "頂呱呱", "速食", "優惠"]
                if any(k in title for k in fastfood_keywords):
                    brand = "綜合/其他"
                    if "麥當勞" in title: brand = "麥當勞"
                    elif "肯氣基" in title or "肯德基" in title: brand = "肯德基"
                    elif "漢堡王" in title: brand = "漢堡王"
                    elif "摩斯" in title: brand = "摩斯漢堡"
                    elif "拿坡里" in title: brand = "拿坡里"
                    elif "必勝客" in title: brand = "必勝客"
                    
                    link = f"https://www.dcard.tw/f/savemoney/p/{post_id}"
                    dcard_deals.append({
                        "brand": brand,
                        "code": "詳見內文",
                        "title": f"💬 Dcard情報：{title}",
                        "content": f"{excerpt[:60]}...\n\n👉 **[點擊前往 Dcard 原文看詳細討論]({link})**",
                        "days_left": 7,
                        "source": "Dcard即時"
                    })
    except Exception as e:
        print(f"Dcard 爬蟲異常: {e}")
    return dcard_deals

# ================= 3. Threads 熱議爆料 (透過 Google 高級搜尋) =================
@st.cache_data(ttl=1800)
def get_threads_deals():
    threads_deals = []
    search_query = 'site:threads.net "優惠碼" OR "代碼" OR "優惠券" (麥當勞 OR 肯德基 OR 漢堡王)'
    url = f"https://www.google.com/search?q={search_query}&num=20"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            search_results = soup.find_all("div", class_="g")
            
            for result in search_results:
                title_tag = result.find("h3")
                link_tag = result.find("a")
                snippet_tag = result.find("div", class_=re.compile("VwiC3b|yXM1m"))
                
                if title_tag and link_tag and snippet_tag:
                    title = title_tag.text
                    link = link_tag["href"]
                    snippet = snippet_tag.text
                    
                    brand = "綜合/其他"
                    if "麥當勞" in title or "麥當勞" in snippet: brand = "麥當勞"
                    elif "肯德基" in title or "肯德基" in snippet: brand = "肯德基"
                    elif "漢堡王" in title or "漢堡王" in snippet: brand = "漢堡王"
                    elif "摩斯" in title or "摩斯" in snippet: brand = "摩斯漢堡"
                    
                    clean_title = title.split(" - Threads")[0].split(" (@")[0]
                    threads_deals.append({
                        "brand": brand,
                        "code": "詳見脆文",
                        "title": f"🧵 Threads熱議：{clean_title}",
                        "content": f"{snippet[:60]}...\n\n👉 **[點擊前往 Threads 脆文看詳細內容]({link})**",
                        "days_left": 5,
                        "source": "Threads即時"
                    })
    except Exception as e:
        print(f"Threads 爬蟲異常: {e}")
    return threads_deals

# ================= 4. 內建隱藏神券數據庫 =================
def get_backup_database():
    return [
        {"brand": "肯德基", "code": "40457", "title": "4塊雞塊買一送一", "content": "4塊上校雞塊買一送一！只要 $49 (原價$98)", "days_left": 90, "source": "精選精選"},
        {"brand": "肯德基", "code": "40558", "title": "大薯買一送一", "content": "香酥脆薯(大)買一送一！只要 $65", "days_left": 90, "source": "精選精選"},
        {"brand": "肯德基", "code": "26593", "title": "雞塊富翁狂歡", "content": "18塊上校雞塊 + 1顆原味蛋撻 + 小薯 + 小綠茶。只要 $120", "days_left": 60, "source": "精選精選"},
        {"brand": "肯德基", "code": "15863", "title": "百元有找解饞餐", "content": "1塊咔啦脆雞 + 4塊上校雞塊 + 中綠茶。只要 $98", "days_left": 45, "source": "精選精選"},
        {"brand": "漢堡王", "code": "P0390", "title": "四塊雞塊買一送一", "content": "4塊雞塊買一送一，兩份只要$65！", "days_left": 120, "source": "精選精選"},
        {"brand": "漢堡王", "code": "P0619", "title": "起士牛堡全餐", "content": "起士牛堡 + 4塊雞塊 + 小薯條 + 中可樂，超值價$109！", "days_left": 90, "source": "精選精選"},
        {"brand": "麥當勞", "code": "1GIFT", "title": "歡樂送買一送一", "content": "網路歡樂送訂餐輸入代碼，享10塊雞塊、大薯或焦糖奶茶買一送一！", "days_left": 30, "source": "精選精選"},
        {"brand": "摩斯漢堡", "code": "臨櫃點購", "title": "大麥珍珠堡套餐", "content": "超級大麥海洋珍珠堡 + 大杯冰紅茶，期間限定特價$115 (原價$130)", "days_left": 60, "source": "精選精選"}
    ]

# ================= UI 介面設計 =================
st.title("🍔 2026 全網速食神券動態雷達")
st.markdown("結合 **Threads熱爆、Dcard省錢板、PTT情報、精選神券** 四大數據來源！")

with st.spinner('雷達正在全面掃描四大平台最新優惠...'):
    ptt_data = get_realtime_deals()
    dcard_data = get_dcard_deals()
    threads_data = get_threads_deals()
    db_data = get_backup_database()
    all_data = ptt_data + dcard_data + threads_data + db_data

# 頂部過濾器
col_b, col_k = st.columns([1, 2])
with col_b:
    brand_filter = st.selectbox(
        "🏪 選擇速食品牌", 
        ["全部品牌", "肯德基", "麥當勞", "漢堡王", "摩斯漢堡", "拿坡里", "必勝客", "綜合/其他"]
    )
with col_k:
    keyword = st.text_input("🔍 輸入關鍵字篩選餐點 (例如：雞塊、買一送一、大薯)")

# 篩選邏輯
display_data = all_data
if brand_filter != "全部品牌":
    display_data = [d for d in display_data if d['brand'] == brand_filter]
if keyword:
    display_data = [d for d in display_data if keyword in d['title'] or keyword in d['content']]

# 排序邏輯：Threads(0) > Dcard(1) > PTT(2) > 精選精選(3)
def get_source_priority(item):
    src = item['source']
    if src == "Threads即時": return 0
    elif src == "Dcard即時": return 1
    elif src == "PTT即時": return 2
    else: return 3

display_data.sort(key=get_source_priority)

st.success(f"✅ 雷達已成功鎖定 **{len(display_data)}** 筆速食優惠資訊！")

# 渲染卡片介面
cols = st.columns(2)
for idx, r in enumerate(display_data):
    with cols[idx % 2]:
        with st.container(border=True):
            st.markdown(f"### 【{r['brand']}】 {r['title']}")
            
            # 社群即時來源提供直接超連結，精選神券提供複製代碼功能
            if r['source'] in ["Threads即時", "Dcard即時", "PTT即時"]:
                st.info(r['content'])
            else:
                st.info(f"**套餐內容：**\n\n{r['content']}")
                st.divider()
                c1, c2 = st.columns([3, 1])
                c1.code(r['code'], language="text")
                c2.caption("👆 點擊代碼複製")

st.markdown("---")
if st.button("🔄 重新清空快取並全面掃描網路"):
    st.cache_data.clear()
    st.rerun()
