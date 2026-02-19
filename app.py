import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, date
import time
import base64
import glob

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Emir Özkök Akademi", layout="wide", page_icon="🧿", initial_sidebar_state="collapsed")

# --- 🏛️ DOSYALAR ---
USER_DATA = "users_secure.csv"  
WORK_DATA = "calisma_verileri.csv"
VIDEO_DATA = "videolar.csv"
TASKS_DATA = "odevler.csv"
BOOKS_DATA = "ogrenci_kitaplari.csv"
GOALS_DATA = "hedefler.csv"
EMIR_QUESTIONS = "emire_gelen_sorular.csv"
SMART_FLASHCARD_DATA = "akilli_kartlar.csv"
TRIALS_DATA = "denemeler.csv"
VIDEO_FOLDER = "ozel_videolar"

# --- YÖNETİCİ BİLGİLERİ ---
ADMIN_USER = "emirozkok"
ADMIN_PASS_RAW = "Hbaamaek7!.zemir" 

# --- 📋 MÜFREDAT ---
CIZELGE_DETAY = {
    "TYT TÜRKÇE": ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Ses Bilgisi", "Yazım Kuralları", "Noktalama", "Sözcük Türleri", "Fiiller", "Cümlenin Ögeleri", "Anlatım Bozukluğu"],
    "TYT TARİH": ["Tarih Bilimine Giriş", "İlk Çağ", "İslamiyet Öncesi Türk", "İslam Tarihi", "Türk İslam", "Osmanlı (Kuruluş-Yükselme)", "Osmanlı (Duraklama-Dağılma)", "Milli Mücadele", "Atatürk İlkeleri"],
    "TYT COĞRAFYA": ["Doğa ve İnsan", "Dünya'nın Şekli", "Coğrafi Konum", "Harita", "İklim", "Yer Şekilleri", "Nüfus", "Ulaşım", "Ekonomik Faaliyetler", "Afetler"],
    "TYT FELSEFE": ["Felsefeye Giriş", "Bilgi", "Varlık", "Ahlak", "Sanat", "Din", "Siyaset", "Bilim"],
    "TYT DİN": ["Bilgi ve İnanç", "Din ve İslam", "İslam ve İbadet", "Hz. Muhammed", "Vahiy ve Akıl"],
    "TYT MATEMATİK": ["Temel Kavramlar", "Sayı Basamakları", "Bölme-Bölünebilme", "EBOB-EKOK", "Rasyonel", "Eşitsizlikler", "Mutlak Değer", "Üslü-Köklü", "Çarpanlara Ayırma", "Oran-Orantı", "Problemler", "Mantık", "Kümeler", "Fonksiyonlar", "Polinomlar", "PKOB"],
    "TYT FİZİK": ["Fizik Bilimi", "Madde ve Özellikleri", "Hareket", "İş-Güç-Enerji", "Isı-Sıcaklık", "Elektrostatik", "Elektrik", "Optik", "Basınç", "Dalgalar"],
    "TYT KİMYA": ["Kimya Bilimi", "Atom", "Türler Arası Etkileşim", "Madden Halleri", "Asit-Baz-Tuz", "Karışımlar", "Kimya Her Yerde"],
    "TYT BİYOLOJİ": ["Canlıların Ortak Öz.", "Temel Bileşenler", "Hücre", "Sınıflandırma", "Bölünmeler", "Kalıtım", "Ekoloji"],
    "GEOMETRİ": ["Üçgenler", "Çokgenler", "Dörtgenler", "Çember-Daire", "Katı Cisimler", "Analitik", "Dönüşüm"],
    "AYT MATEMATİK": ["Fonksiyonlar-2", "Polinomlar-2", "2. Dereceden Denklem", "Parabol", "Eşitsizlikler", "Trigonometri", "Logaritma", "Diziler", "Limit", "Türev", "İntegral"],
    "AYT FİZİK": ["Vektör", "Bağıl Hareket", "Newton", "Atışlar", "İtme-Momentum", "Tork-Denge", "Elektrik-Manyetizma", "Çembersel Hareket", "Harmonik Hareket", "Dalga Mekaniği", "Modern Fizik"],
    "AYT KİMYA": ["Modern Atom", "Gazlar", "Sıvı Çözeltiler", "Enerji", "Hız", "Denge", "Asit-Baz Dengesi", "KÇÇ", "Elektrik", "Organik"],
    "AYT BİYOLOJİ": ["Sistemler", "Komünite", "Genden Proteine", "Canlılık ve Enerji", "Bitki Biyolojisi"],
    "AYT EDEBİYAT": ["Şiir Bilgisi", "Edebi Sanatlar", "İslamiyet Öncesi", "Halk Edebiyatı", "Divan", "Tanzimat", "Servet-i Fünun", "Milli Edebiyat", "Cumhuriyet"],
    "AYT TARİH": ["Tarih Bilimi", "İlk Türk Devletleri", "İslam Tarihi", "Türk-İslam", "Osmanlı Tarihi", "İnkılap Tarihi", "Çağdaş Türk Dünya"],
    "AYT COĞRAFYA": ["Biyoçeşitlilik", "Ekosistem", "Nüfus Politikaları", "Türkiye Ekonomisi", "Kültür Bölgeleri", "Küresel Ticaret", "Çevre Sorunları"]
}

FLASHCARD_DERSLER = list(CIZELGE_DETAY.keys())
ODEV_DERSLERI = list(CIZELGE_DETAY.keys())

# --- 🛡️ GÜVENLİ DOSYA OKUMA ---
def safe_read_csv(file_path, columns):
    try:
        if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
            df = pd.DataFrame(columns=columns)
            df.to_csv(file_path, index=False)
            return df
        return pd.read_csv(file_path)
    except Exception:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)
        return df

def make_hashes(p): return hashlib.sha256(str.encode(p)).hexdigest()

def init_files():
    if not os.path.exists(VIDEO_FOLDER): os.makedirs(VIDEO_FOLDER)
    
    safe_read_csv(WORK_DATA, ["username", "Tarih", "Ders", "Konu", "Soru", "Süre"])
    safe_read_csv(TASKS_DATA, ["id", "username", "book", "ders", "konu", "gorev", "durum", "tarih"])
    safe_read_csv(BOOKS_DATA, ["username", "book_name", "category", "status"])
    safe_read_csv(GOALS_DATA, ["username", "date", "target_min", "status"])
    safe_read_csv(EMIR_QUESTIONS, ["id", "Tarih", "Kullanici", "Soru", "Durum"])
    safe_read_csv(SMART_FLASHCARD_DATA, ["username", "ders", "soru", "cevap", "tarih"])
    safe_read_csv(TRIALS_DATA, ["username", "tarih", "tur", "yayin", "net"])
    safe_read_csv(VIDEO_DATA, ["baslik", "dosya_yolu"])

    if not os.path.exists(USER_DATA) or os.stat(USER_DATA).st_size == 0:
        df = pd.DataFrame(columns=["username", "password", "ad", "telefon", "email", "hedef", "is_coaching", "warnings", "plus"])
        admin_data = pd.DataFrame([[ADMIN_USER, make_hashes(ADMIN_PASS_RAW), "Emir Özkök", "05000000000", "admin@emir.com", "Mühendislik", "True", 0, "True"]], columns=df.columns)
        df = pd.concat([df, admin_data], ignore_index=True)
        df.to_csv(USER_DATA, index=False)
    else:
        try:
            ud = pd.read_csv(USER_DATA)
            if ADMIN_USER in ud['username'].values:
                ud.loc[ud['username'] == ADMIN_USER, 'password'] = make_hashes(ADMIN_PASS_RAW)
                ud['is_coaching'] = ud['is_coaching'].astype(str)
                ud.to_csv(USER_DATA, index=False)
        except: pass

init_files()

# --- 🚀 GLOBAL KRONOMETRE GÖSTERGESİ FONKSİYONU ---
def render_floating_timer():
    if st.session_state.get('timer_active', False) and st.session_state.page != 'kronometre':
        elapsed = st.session_state.elapsed_time + (time.time() - st.session_state.start_time)
        try: 
            gd = safe_read_csv(GOALS_DATA, ["username", "date", "target_min"])
            my_goal = gd[(gd['username']==st.session_state.username) & (gd['date']==str(date.today()))]
            target_val = int(my_goal.iloc[0]['target_min']) if not my_goal.empty else 0
        except: target_val = 0
        
        if target_val > 0:
            remaining = (target_val * 60) - elapsed
            if remaining < 0: remaining = 0
            display_time = remaining
        else:
            display_time = elapsed
            
        m = int(display_time // 60)
        s = int(display_time % 60)
        
        st.markdown(f"""
        <div style='position: fixed; top: 15px; right: 15px; background: linear-gradient(135deg, #f59e0b, #d97706); color: #fff; padding: 10px 20px; border-radius: 12px; font-weight: 800; font-size: 16px; z-index: 99999; box-shadow: 0 4px 20px rgba(245, 158, 11, 0.6); border: 2px solid #fff; animation: pulse 2s infinite;'>
            ⏱️ ODAK AKTİF | {m:02d}:{s:02d}
        </div>
        <style>
        @keyframes pulse {{
            0% {{ transform: scale(1); box-shadow: 0 4px 20px rgba(245, 158, 11, 0.6); }}
            50% {{ transform: scale(1.05); box-shadow: 0 4px 30px rgba(245, 158, 11, 0.9); }}
            100% {{ transform: scale(1); box-shadow: 0 4px 20px rgba(245, 158, 11, 0.6); }}
        }}
        </style>
        """, unsafe_allow_html=True)


# --- 🎨 CSS: GENEL ---
st.markdown("""
<style>
    .stApp { background-color: #02040a; color: #e2e8f0; font-family: 'Inter', sans-serif; }
    header, footer, #MainMenu, .stDeployButton, div[class^='viewerBadge'] {display: none !important;}
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }

    .dashboard-card {
        border-radius: 20px; padding: 20px; color: white;
        transition: transform 0.2s; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: 150px; display: flex; flex-direction: column;
        justify-content: center; align-items: center; text-align: center;
        margin-bottom: 10px; border: none;
    }
    .dashboard-card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px rgba(0,0,0,0.3); }
    .dashboard-card h3 { margin: 0; font-size: 22px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    .dashboard-card p { margin: 5px 0 0 0; font-size: 15px; opacity: 0.95; font-weight: 500; }

    .card-purple { background: linear-gradient(135deg, #9b5de5, #f15bb5); }
    .card-mustard { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); }
    .card-orange { background: linear-gradient(135deg, #ff9966, #ff5e62); }
    .card-blue { background: linear-gradient(135deg, #00c6ff, #0072ff); }
    .card-dark { background: linear-gradient(135deg, #434343, #000000); }
    
    div.stTextInput > div > div > input, div.stSelectbox > div > button, div.stNumberInput > div > div > input { 
        background-color: #1e293b; color: white; border: 1px solid #334155; 
    }
    div.stButton > button { 
        background-color: transparent; color: white; border: 1px solid rgba(255,255,255,0.2); 
        font-weight: bold; width: 100%; transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #3b82f6; border-color: #3b82f6;
    }

    .teams-link {
        display: block; width: 100%; padding: 15px;
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white !important; text-align: center; border-radius: 8px;
        text-decoration: none; font-weight: bold; font-size: 16px;
        margin-top: 20px; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); transition: 0.3s;
    }
    .teams-link:hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5); }
</style>
""", unsafe_allow_html=True)

# --- SESSION ---
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'timer_active' not in st.session_state: st.session_state.timer_active = False
if 'elapsed_time' not in st.session_state: st.session_state.elapsed_time = 0
if 'start_time' not in st.session_state: st.session_state.start_time = 0

def go_to(page): st.session_state.page = page; st.rerun()

# ==========================================
# 1. LANDING PAGE
# ==========================================
if st.session_state.page == 'landing' and not st.session_state.logged_in:
    
    # KUTUYU DİREKT SEKMELERİN (TABS) ÜSTÜNE GİYDİREN PROFESYONEL CSS
    st.markdown("""
    <style>
    /* Sekme panelini (Tabs) neon kutuya çevirir */
    div[data-testid="stTabs"] {
        background: rgba(15, 23, 42, 0.9);
        padding: 25px; 
        border-radius: 20px;
        border: 2px solid #3b82f6; 
        box-shadow: 0 0 40px rgba(59, 130, 246, 0.4);
    }
    /* Giriş ve Kayıt butonlarını tam ortadan (50/50) ikiye böler */
    button[data-baseweb="tab"] {
        flex-grow: 1 !important;
        text-align: center !important;
        justify-content: center !important;
        font-size: 18px !important;
        font-weight: 800 !important;
    }
    /* Altındaki gereksiz çizgileri temizler */
    div[data-baseweb="tab-highlight"] {
        background-color: #3b82f6 !important;
    }
    div[data-baseweb="tab-border"] {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; font-size: 70px; color:#3b82f6; margin-bottom:30px; text-shadow: 0 0 20px rgba(59,130,246,0.5);'>EMİR ÖZKÖK</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div style='text-align:left; margin-bottom: 30px;'>
            <p style='color:#e2e8f0; font-size:22px; line-height:1.6; font-weight: 500;'>
            Sınav senesinde <b>"keşke böyle bir site olsaydı"</b> diyeceğim şekilde, ihtiyaçlarına göre bir site hazırladım.
            </p>
            <p style='color:#94a3b8; font-size:18px; margin-top:20px;'>
            ✅ Yaptıklarını kaydet, gelişimini gör.<br>
            ✅ Ne kadar soru çözdüğünü anlık takip et.<br>
            ✅ Önemli bilgileri not et, flash kartlarla çalış.<br>
            ✅ Denemelerini analiz et ve yükselişe geç!
            </p>
            <p style='color:#3b82f6; font-weight:bold; font-size:26px; margin-top:30px;'>
            HADİ HEMEN BAŞLA! 🚀
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        found_files = glob.glob("emir_foto.*") + glob.glob("emir*.*")
        photo_path = None
        for f in found_files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jpg.jpg')): photo_path = f; break
        
        if photo_path:
            with open(photo_path, "rb") as image_file: encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'''<div style="width:100%; aspect-ratio: 16/9; overflow:hidden; border-radius:20px; border:2px solid #3b82f6; box-shadow: 0 0 30px rgba(59, 130, 246, 0.3);"><img src="data:image/png;base64,{encoded_string}" style="width:100%; height:100%; object-fit:cover;"></div>''', unsafe_allow_html=True)

    with col2:
        # BOŞ DİV'LER SİLİNDİ, SEKMELER DOĞRUDAN OLUŞTURULDU
        tab1, tab2 = st.tabs(["🔐 GİRİŞ YAP", "📝 KAYIT OL"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            u = st.text_input("Kullanıcı Adı", key="l_u")
            p = st.text_input("Şifre", type='password', key="l_p")
            if st.button("GİRİŞ YAP", use_container_width=True):
                try:
                    ud = safe_read_csv(USER_DATA, ["username", "password", "ad", "is_coaching"])
                    hp = make_hashes(p)
                    user = ud[(ud['username']==u) & (ud['password']==hp)]
                    if not user.empty:
                        st.session_state.logged_in=True
                        st.session_state.username=u
                        st.session_state.realname=user.iloc[0]['ad']
                        st.session_state.is_coaching = str(user.iloc[0]['is_coaching']).strip().lower() in ['true', '1', 'yes']
                        st.session_state.page='dashboard'
                        st.rerun()
                    else: st.error("Hatalı bilgiler.")
                except Exception as e: st.error(f"Hata: {e}")
        
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            n = st.text_input("Ad Soyad", key="r_n")
            ru = st.text_input("Kullanıcı Adı", key="r_u")
            rp = st.text_input("Şifre (Min 7 karakter)", type='password', key="r_p")
            rh = st.selectbox("Hedefin (Bölüm)", ["Sayısal", "Eşit Ağırlık", "Sözel", "Dil"], key="r_h")
            rt = st.text_input("Telefon", key="r_t", max_chars=11)
            rm = st.text_input("E-posta", key="r_m")
            
            if st.button("KAYDI TAMAMLA", use_container_width=True):
                if not n or not ru or not rp: st.error("Boş alan bırakma.")
                else:
                    try:
                        ud = safe_read_csv(USER_DATA, ["username", "password", "ad", "telefon", "email", "hedef", "is_coaching"])
                        if ru not in ud['username'].values:
                            new_user = pd.DataFrame([[ru, make_hashes(rp), n, rt, rm, rh, "False", 0, "False"]], columns=ud.columns)
                            pd.concat([ud, new_user], ignore_index=True).to_csv(USER_DATA, index=False)
                            st.success("Kayıt Başarılı! 'Giriş Yap' sekmesine tıkla.")
                        else: st.error("Kullanıcı adı alınmış.")
                    except: st.error("Kayıt hatası.")
        
        st.markdown("""
        <a href="https://teams.live.com/l/community/FEA37u2Ksl3MjtjcgY" target="_blank" class="teams-link">
        🎁 Bedava hazır programlar ve taktikler için TOPLULUĞA KATIL
        </a>
        """, unsafe_allow_html=True)

# ==========================================
# 2. DASHBOARD
# ==========================================
elif st.session_state.logged_in and st.session_state.page == 'dashboard':
    
    render_floating_timer() # SAĞ ÜST KAYAN KRONOMETRE
    
    c1, c2 = st.columns([8, 2])
    with c1: st.markdown(f"## 👋 {st.session_state.realname}")
    with c2: 
        c_b1, c_b2 = st.columns(2)
        with c_b1: 
            if st.button("⚙️"): go_to('settings')
        with c_b2:
            if st.button("ÇIKIŞ"): st.session_state.logged_in=False; st.rerun()
    st.markdown("---")

    try:
        df_w = safe_read_csv(WORK_DATA, ["username", "Soru", "Süre"])
        my_data = df_w[df_w['username'] == st.session_state.username]
        total_solved = my_data['Soru'].sum()
        total_min = my_data['Süre'].sum()
        saat = int(total_min // 60)
        dakika = int(total_min % 60)
        time_str = f"{saat} Sa {dakika} Dk"
    except: total_solved=0; time_str="0 Sa 0 Dk"

    cL, cR = st.columns([1, 2])
    with cL:
        st.markdown(f"""
        <div class='dashboard-card card-blue' style='height: auto; align-items: flex-start; text-align: left; background: #1e293b; border: 1px solid #3b82f6;'>
            <h3 style='color:#3b82f6;'>📊 DURUM RAPORU</h3>
            <p style='font-size:24px; font-weight:bold; color:white; margin-top:10px;'>{int(total_solved)} <span style='font-size:14px; font-weight:normal; color:#aaa;'>Soru</span></p>
            <p style='font-size:24px; font-weight:bold; color:white;'>{time_str} <span style='font-size:14px; font-weight:normal; color:#aaa;'>Süre</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with cR:
        if st.session_state.username == ADMIN_USER: st.success("🎓 YÖNETİCİ PANELİ")
        r1_c1, r1_c2, r1_c3 = st.columns(3)
        with r1_c1:
            st.markdown('<div class="dashboard-card card-purple"><h3>📚 ÖDEV</h3><p>Görev Yönetimi</p></div>', unsafe_allow_html=True)
            if st.session_state.get('is_coaching', False):
                if st.button("GÖREVLERİ AÇ", use_container_width=True): 
                    if st.session_state.username == ADMIN_USER: go_to('admin_cizelge')
                    else: go_to('my_tasks')
            else: st.button("🔒 KİLİTLİ", disabled=True, use_container_width=True)
        with r1_c2:
            st.markdown('<div class="dashboard-card card-mustard"><h3>⏱️ ODAK & HEDEF</h3><p>Kronometre</p></div>', unsafe_allow_html=True)
            if st.button("BAŞLA", use_container_width=True): go_to('kronometre')
        with r1_c3:
            st.markdown('<div class="dashboard-card card-orange"><h3>📊 ANALİZ</h3><p>Toplu Giriş & Denemeler</p></div>', unsafe_allow_html=True)
            if st.button("İNCELE", use_container_width=True): go_to('stats')

        st.markdown("<br>", unsafe_allow_html=True)
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            st.markdown('<div class="dashboard-card card-dark"><h3>💬 SORU SOR</h3><p>Emir Özkök\'e</p></div>', unsafe_allow_html=True)
            if st.button("MESAJ AT", use_container_width=True): go_to('ask_emir')
        with r2_c2:
            st.markdown('<div class="dashboard-card card-purple" style="background: linear-gradient(135deg, #E91E63, #9C27B0);"><h3>🧠 KARTLAR</h3><p>Flashcards</p></div>', unsafe_allow_html=True)
            if st.button("ÇALIŞ", use_container_width=True): go_to('flashcards')

        if st.session_state.username == ADMIN_USER:
            st.markdown("---")
            a1, a2, a3, a4 = st.columns(4)
            with a1: 
                if st.button("KİTAPLARI YÖNET"): go_to('admin_books')
            with a2: 
                if st.button("ÖĞRENCİ LİSTESİ"): go_to('admin_users')
            with a3: 
                if st.button("GELEN MESAJLAR"): go_to('admin_inbox')
            with a4:
                if st.button("💾 YEDEKLE / GERİ YÜKLE"): go_to('admin_backup')

# ==========================================
# 3. İÇ SAYFALAR
# ==========================================
elif st.session_state.logged_in:
    render_floating_timer() # SAĞ ÜST KAYAN KRONOMETRE
    
    c_bk, c_tit = st.columns([1,10])
    with c_bk:
        if st.button("⬅️"): go_to('dashboard')
    
    if st.session_state.page == 'settings':
        st.header("⚙️ Profil Ayarları")
        try:
            ud = safe_read_csv(USER_DATA, ["username", "ad", "telefon", "hedef"])
            curr = ud[ud['username']==st.session_state.username].iloc[0]
            with st.form("settings"):
                na = st.text_input("Ad Soyad", value=curr['ad'])
                nt = st.text_input("Telefon", value=str(curr['telefon']))
                nh = st.selectbox("Hedefin", ["Sayısal", "Eşit Ağırlık", "Sözel", "Dil"], index=0)
                np = st.text_input("Yeni Şifre (İsteğe bağlı)", type='password')
                if st.form_submit_button("GÜNCELLE"):
                    idx = ud[ud['username']==st.session_state.username].index[0]
                    ud.at[idx, 'ad'] = na
                    ud.at[idx, 'telefon'] = nt
                    ud.at[idx, 'hedef'] = nh
                    if np and len(np)>6: ud.at[idx, 'password'] = make_hashes(np)
                    ud.to_csv(USER_DATA, index=False)
                    st.session_state.realname = na
                    st.success("Bilgiler güncellendi!"); time.sleep(1); st.rerun()
        except: st.error("Ayar hatası")

    elif st.session_state.page == 'admin_users':
        st.header("👥 Öğrenci Yönetimi")
        st.info("❗ Koçluk yetkisi vermek için 'is_coaching' kutucuğunu işaretle ve KAYDET butonuna bas.")
        ud = safe_read_csv(USER_DATA, ["username", "is_coaching"])
        ud['is_coaching'] = ud['is_coaching'].apply(lambda x: str(x).lower() in ['true', '1', 'yes'])
        edited_df = st.data_editor(ud, num_rows="dynamic", column_config={"is_coaching": st.column_config.CheckboxColumn("Koçluk Öğrencisi mi?", default=False)})
        if st.button("💾 DEĞİŞİKLİKLERİ KAYDET"):
            edited_df['is_coaching'] = edited_df['is_coaching'].astype(str)
            edited_df.to_csv(USER_DATA, index=False)
            st.success("Veriler güncellendi!")
            time.sleep(1); st.rerun()

    elif st.session_state.page == 'stats':
        st.header("📊 Analiz ve Veri Girişi")
        tab_calisma, tab_deneme, tab_grafik = st.tabs(["📚 GÜNLÜK ÇALIŞMA", "🏆 DENEME SINAVI", "📈 GRAFİKLER"])
        
        with tab_calisma:
            st.subheader("1. Soru Girişi (Tüm Dersler)")
            st.info("Bugün çözdüğün soruları aşağıdaki listeden girip tek seferde kaydet.")
            selected_date = st.date_input("Hangi Tarih?", date.today())
            
            if 'bulk_data' not in st.session_state:
                baslangic_verisi = [{"Ders": d, "Soru": 0} for d in list(CIZELGE_DETAY.keys())]
                st.session_state.bulk_data = pd.DataFrame(baslangic_verisi)

            edited_table = st.data_editor(
                st.session_state.bulk_data,
                hide_index=True,
                column_config={
                    "Ders": st.column_config.TextColumn("Ders", disabled=True), 
                    "Soru": st.column_config.NumberColumn("Soru Sayısı", min_value=0, step=1)
                },
                use_container_width=True
            )
            
            if st.button("💾 LİSTEYİ KAYDET", type="primary"):
                try: df = safe_read_csv(WORK_DATA, ["username","Tarih","Ders","Konu","Soru","Süre"])
                except: df = pd.DataFrame(columns=["username","Tarih","Ders","Konu","Soru","Süre"])
                
                new_entries = []
                for index, row in edited_table.iterrows():
                    if row["Soru"] > 0:
                        new_entries.append({
                            "username": st.session_state.username,
                            "Tarih": str(selected_date),
                            "Ders": row["Ders"],
                            "Konu": "Soru Çözümü",
                            "Soru": row["Soru"],
                            "Süre": 0
                        })
                
                if new_entries:
                    new_df = pd.DataFrame(new_entries)
                    df = pd.concat([df, new_df], ignore_index=True)
                    df.to_csv(WORK_DATA, index=False)
                    st.success(f"✅ {len(new_entries)} ders kaydedildi!")
                    st.session_state.bulk_data = pd.DataFrame([{"Ders": d, "Soru": 0} for d in list(CIZELGE_DETAY.keys())])
                    time.sleep(1); st.rerun()
                else: st.warning("Soru sayısı girmedin.")

            st.write("---")
            st.subheader("2. Günlük Toplam Süre")
            c_h, c_m, c_b = st.columns([1, 1, 1])
            saat = c_h.number_input("Saat", 0, 24, 0)
            dakika = c_m.number_input("Dakika", 0, 59, 0)
            if c_b.button("Süreyi Kaydet"):
                toplam_dk = (saat * 60) + dakika
                if toplam_dk > 0:
                    df = safe_read_csv(WORK_DATA, ["username","Tarih","Ders","Konu","Soru","Süre"])
                    new_row = pd.DataFrame([[st.session_state.username, str(selected_date), "GENEL", "Günlük Süre", 0, toplam_dk]], columns=df.columns)
                    pd.concat([df, new_row], ignore_index=True).to_csv(WORK_DATA, index=False)
                    st.success(f"Toplam {saat} saat {dakika} dakika kaydedildi!")
                else: st.warning("Süre girmedin.")

        with tab_deneme:
            st.subheader("🏆 Deneme Sınavı Ekle")
            with st.form("trial_form"):
                c_t1, c_t2 = st.columns(2)
                t_date = c_t1.date_input("Deneme Tarihi", date.today())
                t_tur = c_t2.selectbox("Deneme Türü", ["TYT", "AYT", "Branş Denemesi"])
                c_t3, c_t4 = st.columns(2)
                t_yayin = c_t3.text_input("Yayın Evi (Örn: 345, Bilgi Sarmal)")
                t_net = c_t4.number_input("Toplam Net", min_value=0.0, step=0.25, format="%.2f")
                if st.form_submit_button("DENEMEYİ KAYDET"):
                    trial_df = safe_read_csv(TRIALS_DATA, ["username", "tarih", "tur", "yayin", "net"])
                    new_trial = pd.DataFrame([[st.session_state.username, str(t_date), t_tur, t_yayin, t_net]], columns=trial_df.columns)
                    pd.concat([trial_df, new_trial], ignore_index=True).to_csv(TRIALS_DATA, index=False)
                    st.success("✅ Deneme kaydedildi!")
                    time.sleep(1); st.rerun()
            st.write("### 📉 Deneme Grafiği")
            try:
                tdf = safe_read_csv(TRIALS_DATA, ["username", "tarih", "net"])
                my_trials = tdf[tdf['username'] == st.session_state.username]
                if not my_trials.empty:
                    st.line_chart(my_trials, x="tarih", y="net")
                    st.dataframe(my_trials.sort_values(by="tarih", ascending=False), use_container_width=True)
                else: st.info("Henüz deneme kaydı yok.")
            except: st.error("Veri yok.")

        with tab_grafik:
            try:
                df = safe_read_csv(WORK_DATA, ["username", "Ders", "Soru", "Tarih"])
                my_data = df[df['username'] == st.session_state.username]
                if not my_data.empty:
                    st.write("### 📊 Ders Bazlı Soru Dağılımı")
                    chart_data = my_data[my_data['Ders'] != "GENEL"]
                    st.bar_chart(chart_data.groupby("Ders")["Soru"].sum())
                    st.write("### 🗓️ Son Çalışmalar")
                    st.dataframe(my_data.sort_values(by="Tarih", ascending=False).head(10), use_container_width=True)
                else: st.info("Henüz veri yok.")
            except: st.error("Veri okuma hatası.")

    elif st.session_state.page == 'kronometre':
        st.header("⏱️ Odaklanma & Hedef")
        c_k1, c_k2 = st.columns([1, 1])
        
        try: 
            gd = safe_read_csv(GOALS_DATA, ["username", "date", "target_min"])
            my_goal = gd[(gd['username']==st.session_state.username) & (gd['date']==str(date.today()))]
            target_val = int(my_goal.iloc[0]['target_min']) if not my_goal.empty else 0
        except: target_val = 0

        with c_k1:
            st.subheader("🎯 Günlük Hedefin")
            new_target = st.number_input("Bugün kaç dakika çalışacaksın?", value=int(target_val), step=10)
            if st.button("Hedefi Güncelle"):
                gd = safe_read_csv(GOALS_DATA, ["username","date","target_min","status"])
                gd = gd[~((gd['username']==st.session_state.username) & (gd['date']==str(date.today())))]
                new_row = pd.DataFrame([[st.session_state.username, str(date.today()), new_target, "Set"]], columns=gd.columns)
                pd.concat([gd, new_row], ignore_index=True).to_csv(GOALS_DATA, index=False)
                st.success("Hedef belirlendi!")
                time.sleep(0.5); st.rerun()

        with c_k2:
            st.subheader("⏱️ Kronometre")
            t_ders = st.selectbox("Hangi derse çalışıyorsun?", list(CIZELGE_DETAY.keys()), key="timer_lesson")
            c_btn1, c_btn2, c_btn3 = st.columns(3)
            
            if c_btn1.button("▶️ BAŞLAT"):
                st.session_state.timer_active = True
                st.session_state.start_time = time.time()
                st.rerun()
            if c_btn2.button("⏸️ DURDUR"):
                if st.session_state.timer_active:
                    st.session_state.elapsed_time += time.time() - st.session_state.start_time
                    st.session_state.timer_active = False
                st.rerun()
            if c_btn3.button("💾 BİTİR VE KAYDET"):
                final_time = st.session_state.elapsed_time
                if st.session_state.timer_active: final_time += time.time() - st.session_state.start_time
                minutes = int(final_time / 60)
                if minutes > 0:
                    df = safe_read_csv(WORK_DATA, ["username","Tarih","Ders","Konu","Soru","Süre"])
                    new_row = pd.DataFrame([[st.session_state.username, str(date.today()), t_ders, "Kronometre", 0, minutes]], columns=df.columns)
                    pd.concat([df, new_row], ignore_index=True).to_csv(WORK_DATA, index=False)
                    st.success(f"{minutes} dakika kaydedildi!")
                st.session_state.elapsed_time = 0
                st.session_state.timer_active = False
                st.rerun()
            
            elapsed = st.session_state.elapsed_time
            if st.session_state.timer_active:
                elapsed += time.time() - st.session_state.start_time
            
            if target_val > 0:
                remaining = (target_val * 60) - elapsed
                if remaining <= 0:
                    remaining = 0
                    if st.session_state.timer_active:
                        st.session_state.timer_active = False
                        st.session_state.elapsed_time = target_val * 60
                        st.success("🎯 HEDEF SÜREYE ULAŞTIN! Lütfen süreni kaydet.")
                display_time = remaining
            else:
                display_time = elapsed

            mins = int(display_time // 60)
            secs = int(display_time % 60)
            st.markdown(f"<h1 style='font-size: 80px; color: #3b82f6; text-align:center;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
            
            if st.session_state.timer_active:
                time.sleep(1); st.rerun()

    elif st.session_state.page == 'admin_cizelge':
        st.header("Ödev Atama Merkezi")
        users = safe_read_csv(USER_DATA, ["username", "is_coaching"])
        st_list = users[(users['username'] != ADMIN_USER) & (users['is_coaching'].apply(lambda x: str(x).strip().lower() in ['true', '1', 'yes']))]['username'].tolist()
        if st_list:
            target = st.selectbox("Öğrenci Seç", st_list)
            st.write(f"### 📋 {target} - Ödev Geçmişi")
            try:
                td = safe_read_csv(TASKS_DATA, ["username", "tarih", "ders", "konu", "gorev", "durum"])
                past_tasks = td[td['username'] == target][['tarih', 'ders', 'konu', 'gorev', 'durum']]
                st.dataframe(past_tasks.sort_values(by="tarih", ascending=False), use_container_width=True)
            except: st.write("Henüz ödev kaydı yok.")
            st.write("---")
            with st.expander("➕ Yeni Kitap Ekle"):
                bn = st.text_input("Kitap Adı")
                bc = st.selectbox("Ders", list(CIZELGE_DETAY.keys()), key="new_book_lesson")
                if st.button("Kitabı Ekle"):
                    bd = safe_read_csv(BOOKS_DATA, ["username", "book_name", "category", "status"])
                    pd.concat([bd, pd.DataFrame([[target, bn, bc, "Active"]], columns=bd.columns)]).to_csv(BOOKS_DATA, index=False)
                    st.success("Kitap eklendi!")
            st.subheader("📝 Yeni Ödev Ver")
            try: 
                bd = safe_read_csv(BOOKS_DATA, ["username", "book_name"])
                bks = bd[bd['username']==target]['book_name'].tolist()
            except: bks = []
            if bks:
                c1, c2, c3 = st.columns(3)
                s_kitap = c1.selectbox("Kitap", bks)
                s_ders = c2.selectbox("Ders", ODEV_DERSLERI, key="assign_task_lesson")
                s_konu = c3.selectbox("Konu", CIZELGE_DETAY[s_ders])
                s_detay = st.text_input("Detay (Test No / Sayfa)")
                if st.button("ÖDEVİ GÖNDER", use_container_width=True):
                    td = safe_read_csv(TASKS_DATA, ["id", "username", "book", "ders", "konu", "gorev", "durum", "tarih"])
                    new_task = pd.DataFrame([[int(time.time()), target, s_kitap, s_ders, s_konu, s_detay, "Yapılmadı", str(date.today())]], columns=td.columns)
                    pd.concat([td, new_task], ignore_index=True).to_csv(TASKS_DATA, index=False)
                    st.success("Ödev gönderildi!")
            else: st.warning("Önce kitap eklemelisin.")
        else: st.warning("Hiç koçluk öğrencisi yok veya filtre hatası. 'Öğrenci Listesi'nden yetki ver.")

    elif st.session_state.page == 'my_tasks':
        st.header("Ödevlerim")
        try: 
            td = safe_read_csv(TASKS_DATA, ["id", "username", "durum", "ders", "konu", "book", "gorev", "tarih"])
            my = td[td['username']==st.session_state.username]
            if my.empty: st.info("Yapılacak ödevin yok!")
            else:
                my = my.sort_values(by="durum", ascending=False)
                for i, r in my.iterrows():
                    if r['durum'] == 'Yapılmadı':
                        st.error(f"📌 {r['ders']} - {r['konu']}")
                        c1, c2 = st.columns([4,1])
                        c1.write(f"📖 {r['book']} | 📝 {r['gorev']}")
                        if c2.button("BİTİR", key=f"tsk_{r['id']}"):
                            td.loc[td['id']==r['id'], 'durum'] = 'Tamamlandı'
                            td.to_csv(TASKS_DATA, index=False)
                            st.rerun()
                    else:
                        with st.expander(f"✅ {r['ders']} - {r['konu']} (Tamamlandı)"):
                            st.write(f"Kitap: {r['book']} | Görev: {r['gorev']}")
                            st.caption(f"Veriliş Tarihi: {r['tarih']}")
        except: st.info("Sistem hazırlanıyor.")

    elif st.session_state.page == 'ask_emir':
        st.header("Emir Özkök'e Soru Sor")
        q = st.text_area("Mesajın")
        if st.button("Gönder"):
            try: Eq = safe_read_csv(EMIR_QUESTIONS, ["id", "Tarih", "Kullanici", "Soru", "Durum"])
            except: Eq=pd.DataFrame(columns=["id","Tarih","Kullanici","Soru","Durum"])
            pd.concat([Eq, pd.DataFrame([[int(time.time()), str(date.today()), st.session_state.username, q, "Sent"]], columns=Eq.columns)]).to_csv(EMIR_QUESTIONS, index=False); st.success("Mesaj iletildi")

    elif st.session_state.page == 'flashcards':
        st.header("🧠 Akıllı Kartlar")
        t1, t2, t3 = st.tabs(["➕ Kart Ekle", "📖 Serbest Çalış", "🚀 Test Et (Quiz)"])
        
        with t1:
            st.subheader("Yeni Bilgi Ekle")
            d = st.selectbox("Ders", FLASHCARD_DERSLER)
            q = st.text_input("Soru (Ön Yüz)")
            a = st.text_input("Cevap (Arka Yüz)")
            if st.button("Kartı Ekle"):
                fd = safe_read_csv(SMART_FLASHCARD_DATA, ["username", "ders", "soru", "cevap", "tarih"])
                pd.concat([fd, pd.DataFrame([[st.session_state.username,d,q,a,str(date.today())]], columns=fd.columns)]).to_csv(SMART_FLASHCARD_DATA, index=False)
                st.success("Kart başarıyla eklendi!")

        with t2:
            st.subheader("Serbest Kart Okuma")
            try:
                if 'free_card_idx' not in st.session_state: st.session_state.free_card_idx = 0
                if 'free_show_ans' not in st.session_state: st.session_state.free_show_ans = False

                fd = safe_read_csv(SMART_FLASHCARD_DATA, ["username", "ders", "soru", "cevap"])
                my = fd[fd['username']==st.session_state.username]
                
                if not my.empty:
                    if st.session_state.free_card_idx >= len(my): st.session_state.free_card_idx = 0
                    row = my.iloc[st.session_state.free_card_idx]
                    
                    st.markdown(f"<div class='dashboard-card'><h2>{row['soru']}</h2></div>", unsafe_allow_html=True)
                    if st.session_state.free_show_ans: 
                        st.success(f"**Cevap:** {row['cevap']}")
                    
                    c1, c2 = st.columns(2)
                    if c1.button("Cevabı Gör", key="free_see"): 
                        st.session_state.free_show_ans = True
                        st.rerun()
                    if c2.button("Sıradaki Kart", key="free_next"): 
                        st.session_state.free_card_idx += 1
                        st.session_state.free_show_ans = False
                        st.rerun()
                else: st.warning("Henüz kart eklemedin.")
            except: st.error("Kartlar yüklenemedi.")

        with t3:
            st.subheader("Quizlet Modu (Öğrenene Kadar Sorar)")
            if 'test_queue' not in st.session_state:
                st.session_state.test_queue = []
                st.session_state.test_active = False
                st.session_state.test_show_ans = False

            if not st.session_state.test_active:
                st.info("Kendi eklediğin kartlarla test başlar. Bilemediğin kartlar destenin sonuna atılır, öğrenene kadar karşına çıkar.")
                if st.button("🚀 Testi Başlat", use_container_width=True):
                    fd = safe_read_csv(SMART_FLASHCARD_DATA, ["username", "ders", "soru", "cevap"])
                    my = fd[fd['username']==st.session_state.username]
                    if not my.empty:
                        st.session_state.test_queue = my.to_dict('records')
                        st.session_state.test_active = True
                        st.session_state.test_show_ans = False
                        st.rerun()
                    else: st.warning("Testi başlatmak için önce kart eklemelisin!")
            else:
                if len(st.session_state.test_queue) == 0:
                    st.success("🎉 TEBRİKLER! Tüm kartları başarıyla öğrendin!")
                    if st.button("🔄 Testi Yeniden Başlat"):
                        st.session_state.test_active = False
                        st.rerun()
                else:
                    current_card = st.session_state.test_queue[0]
                    st.markdown(f"<div class='dashboard-card card-purple'><h2>{current_card['soru']}</h2></div>", unsafe_allow_html=True)
                    
                    if not st.session_state.test_show_ans:
                        st.text_input("Cevabını Yaz (Sadece kendini denemek için, zorunlu değil):", key="quiz_input")
                        if st.button("Cevabı Kontrol Et", use_container_width=True):
                            st.session_state.test_show_ans = True
                            st.rerun()
                    else:
                        st.info(f"💡 **Asıl Cevap:** {current_card['cevap']}")
                        st.write("Kendini değerlendir:")
                        c_yes, c_no = st.columns(2)
                        
                        if c_yes.button("✅ Bildim (Geç)", use_container_width=True):
                            st.session_state.test_queue.pop(0)
                            st.session_state.test_show_ans = False
                            st.rerun()
                            
                        if c_no.button("❌ Bilemedim (Tekrar Sor)", use_container_width=True):
                            card_to_move = st.session_state.test_queue.pop(0)
                            st.session_state.test_queue.append(card_to_move)
                            st.session_state.test_show_ans = False
                            st.rerun()

    elif st.session_state.page == 'admin_inbox':
        st.header("Gelen Kutusu")
        try: st.dataframe(safe_read_csv(EMIR_QUESTIONS, ["id", "Tarih", "Kullanici", "Soru", "Durum"]))
        except: st.write("Mesaj yok")
    
    elif st.session_state.page == 'admin_books':
        st.header("Öğrenci Kitapları")
        try: st.dataframe(safe_read_csv(BOOKS_DATA, ["username", "book_name"]))
        except: st.write("Kitap yok")

    elif st.session_state.page == 'admin_backup':
        st.header("💾 YEDEKLEME VE GERİ YÜKLEME MERKEZİ")
        st.warning("⚠️ Streamlit sunucusu yeniden başladığında veriler silinebilir. Buradan düzenli olarak dosyaları indir!")
        c_down, c_up = st.columns(2)
        with c_down:
            st.subheader("⬇️ 1. Verileri İndir (Yedekle)")
            files_to_download = [USER_DATA, TASKS_DATA, WORK_DATA, BOOKS_DATA, GOALS_DATA, TRIALS_DATA]
            for f in files_to_download:
                if os.path.exists(f):
                    with open(f, "rb") as file:
                        st.download_button(label=f"📥 İNDİR: {f}", data=file, file_name=f, mime="text/csv")
        with c_up:
            st.subheader("⬆️ 2. Verileri Geri Yükle (Kurtar)")
            st.info("Eğer site sıfırlanırsa, indirdiğin dosyayı buraya yükle.")
            uploaded_file = st.file_uploader("Yedek Dosyayı Seç (Örn: users_secure.csv)", type="csv")
            if uploaded_file is not None:
                original_name = uploaded_file.name
                if st.button(f"♻️ {original_name} DOSYASINI GERİ YÜKLE"):
                    try:
                        df_upload = pd.read_csv(uploaded_file)
                        df_upload.to_csv(original_name, index=False)
                        st.success(f"✅ {original_name} başarıyla geri yüklendi! Sayfayı yenile.")
                    except Exception as e: st.error(f"Hata: {e}")
