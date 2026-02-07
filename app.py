import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, date
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Emir Özkök Akademi", layout="wide", page_icon="🧿", initial_sidebar_state="collapsed")

# --- 🏛️ DOSYALAR (YENİ VERİTABANI: users_secure.csv) ---
USER_DATA = "users_secure.csv"  
WORK_DATA = "calisma_verileri.csv"
VIDEO_DATA = "videolar.csv"
TASKS_DATA = "odevler.csv"
BOOKS_DATA = "ogrenci_kitaplari.csv"
GOALS_DATA = "hedefler.csv"
EMIR_QUESTIONS = "emire_gelen_sorular.csv"
SMART_FLASHCARD_DATA = "akilli_kartlar.csv"
VIDEO_FOLDER = "ozel_videolar"

# --- YÖNETİCİ BİLGİLERİ ---
ADMIN_USER = "emirozkok"
ADMIN_PASS_RAW = "Hbaamaek7!.zemir" 

# --- 📋 LİSTELER ---
HEDEFLER_LISTESI = ["Tıp", "Mühendislik", "Diş Hekimliği", "Hukuk", "Psikoloji", "Yazılım/Bilgisayar", "Mimarlık", "Pilotaj", "Eczacılık", "Diğer"]

# --- FONKSİYONLAR ---
def make_hashes(p): return hashlib.sha256(str.encode(p)).hexdigest()

def init_files():
    if not os.path.exists(VIDEO_FOLDER): os.makedirs(VIDEO_FOLDER)
    files = [WORK_DATA, VIDEO_DATA, TASKS_DATA, BOOKS_DATA, GOALS_DATA, EMIR_QUESTIONS, SMART_FLASHCARD_DATA]
    
    # --- KULLANICI DOSYASI KONTROLÜ ---
    if not os.path.exists(USER_DATA):
        df = pd.DataFrame(columns=["username", "password", "ad", "telefon", "email", "hedef", "is_coaching", "warnings", "plus"])
        
        # SENİ EKLEYEN KOD
        admin_data = pd.DataFrame([[
            ADMIN_USER, 
            make_hashes(ADMIN_PASS_RAW), 
            "Emir Özkök", 
            "05000000000", 
            "admin@emir.com", 
            "Mühendislik", 
            "True", 
            0, 
            "True"
        ]], columns=df.columns)
        
        df = pd.concat([df, admin_data], ignore_index=True)
        df.to_csv(USER_DATA, index=False)
    
    else:
        try:
            ud = pd.read_csv(USER_DATA)
            if ADMIN_USER in ud['username'].values:
                ud.loc[ud['username'] == ADMIN_USER, 'password'] = make_hashes(ADMIN_PASS_RAW)
                ud.to_csv(USER_DATA, index=False)
        except: pass

    for f in files:
        if not os.path.exists(f): pd.DataFrame().to_csv(f, index=False)

init_files()

# --- 🎨 CSS ---
st.markdown("""
<style>
    .stApp { background-color: #02040a; color: #e2e8f0; font-family: 'Inter', sans-serif; }
    
    /* GİZLEME KODLARI */
    header, footer, #MainMenu, .stDeployButton, div[class^='viewerBadge'] {display: none !important;}
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }

    /* KART TASARIMI */
    .dashboard-card {
        border-radius: 20px; padding: 20px; color: white;
        transition: transform 0.2s; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: 150px; display: flex; flex-direction: column;
        justify-content: center; align-items: center; text-align: center;
        margin-bottom: 10px; border: none;
        background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid #334155;
    }
    .dashboard-card:hover { transform: translateY(-5px); border-color: #3b82f6; }
    
    /* INPUTLAR */
    .login-box {
        background: #0f172a; padding: 40px; border-radius: 12px;
        border: 1px solid #1e293b; box-shadow: 0 10px 40px rgba(0,0,0,0.7); margin-top: 20px;
    }
    div.stTextInput > div > div > input, div.stSelectbox > div > button { background-color: #1e293b; color: white; border: 1px solid #334155; }
    div.stButton > button { background-color: #2563eb; color: white; border: none; font-weight: bold; width: 100%; padding: 10px; border-radius: 5px; }
    div.stButton > button:hover { background-color: #1d4ed8; }
</style>
""", unsafe_allow_html=True)

# --- SESSION ---
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def go_to(page): st.session_state.page = page; st.rerun()

# ==========================================
# 1. LANDING PAGE
# ==========================================
if st.session_state.page == 'landing' and not st.session_state.logged_in:
    
    st.markdown("<h1 style='text-align:center; color:#3b82f6;'>EMİR ÖZKÖK</h1>", unsafe_allow_html=True)
    # BURADAKİ YAZIYI SİLDİM
    st.markdown("---")

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.subheader("🔐 GİRİŞ YAP")
        u = st.text_input("Kullanıcı Adı", key="l_u")
        p = st.text_input("Şifre", type='password', key="l_p")
        if st.button("GİRİŞ"):
            try:
                ud = pd.read_csv(USER_DATA)
                hp = make_hashes(p)
                user = ud[(ud['username']==u) & (ud['password']==hp)]
                if not user.empty:
                    st.session_state.logged_in=True
                    st.session_state.username=u
                    st.session_state.realname=user.iloc[0]['ad']
                    st.session_state.is_coaching = (str(user.iloc[0]['is_coaching']) == "True")
                    st.session_state.page='dashboard'
                    st.rerun()
                else: st.error("Hatalı bilgiler.")
            except: st.error("Sistem başlatılıyor, tekrar dene.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.subheader("📝 KAYIT OL")
        n = st.text_input("Ad Soyad", key="r_n")
        ru = st.text_input("Kullanıcı Adı", key="r_u")
        rp = st.text_input("Şifre (Min 7 karakter)", type='password', key="r_p")
        rh = st.selectbox("Hedefin (Bölüm)", HEDEFLER_LISTESI, key="r_h")
        rt = st.text_input("Telefon", key="r_t", max_chars=11)
        rm = st.text_input("E-posta", key="r_m")
        
        if st.button("KAYDOL"):
            if not n or not ru or not rp or not rt or not rm: st.error("Tüm alanları doldur.")
            elif len(rp) < 7: st.error("Şifre çok kısa.")
            else:
                try:
                    ud = pd.read_csv(USER_DATA)
                    if ru not in ud['username'].values:
                        new_user = pd.DataFrame([[ru, make_hashes(rp), n, rt, rm, rh, "False", 0, "False"]], columns=ud.columns)
                        pd.concat([ud, new_user], ignore_index=True).to_csv(USER_DATA, index=False)
                        st.success("Kayıt Başarılı! Soldan giriş yap.")
                    else: st.error("Bu kullanıcı adı alınmış.")
                except: st.error("Veritabanı hatası.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 2. DASHBOARD
# ==========================================
elif st.session_state.logged_in and st.session_state.page == 'dashboard':
    
    c1, c2 = st.columns([8, 2])
    with c1: st.markdown(f"## 👋 Hoş geldin, {st.session_state.realname}")
    with c2: 
        if st.button("ÇIKIŞ"): st.session_state.logged_in=False; st.rerun()
        if st.button("⚙️ AYARLAR"): go_to('settings')
    
    st.write("---")
    
    # YÖNETİCİ PANELİ
    if st.session_state.username == ADMIN_USER:
        st.info("🎓 YÖNETİCİ MODU")
        a1, a2, a3 = st.columns(3)
        with a1:
             st.markdown("<div class='dashboard-card'><h3>👥 Öğrenciler</h3></div>", unsafe_allow_html=True)
             if st.button("Öğrenci Listesi"): go_to('admin_users')
        with a2:
             st.markdown("<div class='dashboard-card'><h3>📚 Ödev Ata</h3></div>", unsafe_allow_html=True)
             if st.button("Ödev Paneli"): go_to('admin_cizelge')
        with a3:
             st.markdown("<div class='dashboard-card'><h3>📩 Mesajlar</h3></div>", unsafe_allow_html=True)
             if st.button("Gelen Kutusu"): go_to('admin_inbox')
    
    st.write("")
    
    # GENEL MENÜ
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown("<div class='dashboard-card'><h3>📊 İstatistik</h3></div>", unsafe_allow_html=True)
        if st.button("Analiz"): go_to('stats')
    with r2:
        st.markdown("<div class='dashboard-card'><h3>⏱️ Kronometre</h3></div>", unsafe_allow_html=True)
        if st.button("Çalışmaya Başla"): go_to('kronometre')
    with r3:
        st.markdown("<div class='dashboard-card'><h3>🎯 Hedefim</h3></div>", unsafe_allow_html=True)
        if st.button("Hedef Gör"): go_to('goals')

# ==========================================
# 3. DİĞER SAYFALAR
# ==========================================
elif st.session_state.logged_in:
    c_bk, c_tit = st.columns([1,10])
    with c_bk:
        if st.button("⬅️"): go_to('dashboard')
    
    if st.session_state.page == 'settings':
        st.header("⚙️ Profil Ayarları")
        try:
            ud = pd.read_csv(USER_DATA)
            curr = ud[ud['username']==st.session_state.username].iloc[0]
            
            with st.form("settings"):
                na = st.text_input("Ad Soyad", value=curr['ad'])
                nt = st.text_input("Telefon", value=str(curr['telefon']))
                nh = st.selectbox("Hedefin", HEDEFLER_LISTESI, index=0)
                np = st.text_input("Yeni Şifre (İsteğe bağlı)", type='password')
                
                if st.form_submit_button("GÜNCELLE"):
                    idx = ud[ud['username']==st.session_state.username].index[0]
                    ud.at[idx, 'ad'] = na
                    ud.at[idx, 'telefon'] = nt
                    ud.at[idx, 'hedef'] = nh
                    if np and len(np)>6: ud.at[idx, 'password'] = make_hashes(np)
                    ud.to_csv(USER_DATA, index=False)
                    st.session_state.realname = na
                    st.success("Bilgiler güncellendi!")
                    time.sleep(1); st.rerun()
        except: st.error("Ayar hatası")

    elif st.session_state.page == 'admin_users':
        st.header("Kayıtlı Öğrenciler")
        try: st.dataframe(pd.read_csv(USER_DATA))
        except: st.write("Veri yok")

    elif st.session_state.page == 'stats':
        st.header("İstatistikler")
        try:
            df = pd.read_csv(WORK_DATA)
            my = df[df['username']==st.session_state.username]
            st.metric("Toplam Çalışma", f"{int(my['Süre'].sum())} dk")
        except: st.write("Henüz veri yok.")

    elif st.session_state.page == 'kronometre':
        st.header("Kronometre")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("BAŞLAT/DURDUR"): st.info("Sayaç çalışıyor...")
        with c2:
            st.title("00:00")
