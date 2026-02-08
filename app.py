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
VIDEO_FOLDER = "ozel_videolar"

# --- YÖNETİCİ BİLGİLERİ ---
ADMIN_USER = "emirozkok"
ADMIN_PASS_RAW = "Hbaamaek7!.zemir" 

# --- 📋 MÜFREDAT (TAM LİSTE) ---
CIZELGE_DETAY = {
    "TYT MATEMATİK": ["Temel Kavramlar", "Sayı Basamakları", "Bölme-Bölünebilme", "EBOB-EKOK", "Rasyonel Sayılar", "Basit Eşitsizlikler", "Mutlak Değer", "Üslü Sayılar", "Köklü Sayılar", "Çarpanlara Ayırma", "Oran-Orantı", "Problemler (Tümü)", "Mantık", "Kümeler", "Fonksiyonlar", "Polinomlar", "Permütasyon-Kombinasyon-Olasılık"],
    "AYT MATEMATİK": ["Fonksiyonlar (II)", "Polinomlar (II)", "2. Dereceden Denklemler", "Parabol", "Eşitsizlikler", "Trigonometri", "Logaritma", "Diziler", "Limit", "Türev", "İntegral"],
    "GEOMETRİ (TYT-AYT)": ["Üçgenler", "Çokgenler", "Dörtgenler", "Özel Dörtgenler", "Çember ve Daire", "Katı Cisimler", "Analitik Geometri", "Dönüşüm Geometrisi", "Çemberin Analitiği"],
    "TYT FİZİK": ["Fizik Bilimine Giriş", "Madde ve Özellikleri", "Hareket ve Kuvvet", "Enerji", "Isı ve Sıcaklık", "Elektrostatik", "Elektrik Akımı", "Optik", "Basınç ve Kaldırma", "Dalgalar"],
    "AYT FİZİK": ["Vektörler", "Bağıl Hareket", "Newton'un Yasaları", "Atışlar", "İş-Güç-Enerji", "İtme ve Momentum", "Tork ve Denge", "Elektrik ve Manyetizma", "Çembersel Hareket", "Basit Harmonik Hareket", "Dalga Mekaniği", "Modern Fizik"],
    "TYT KİMYA": ["Kimya Bilimi", "Atom ve Periyodik Sistem", "Türler Arası Etkileşim", "Maddenin Halleri", "Doğa ve Kimya", "Kimyanın Kanunları", "Mol", "Karışımlar", "Asit-Baz-Tuz", "Kimya Her Yerde"],
    "AYT KİMYA": ["Modern Atom Teorisi", "Gazlar", "Sıvı Çözeltiler", "Enerji", "Hız", "Denge", "Asit-Baz Dengesi", "KÇÇ", "Elektrokimya", "Organik Kimya"],
    "TYT BİYOLOJİ": ["Canlıların Ortak Özellikleri", "Temel Bileşenler", "Hücre", "Sınıflandırma", "Bölünmeler", "Kalıtım", "Ekoloji"],
    "AYT BİYOLOJİ": ["Sistemler (Sinir, Endokrin, Duyu, Destek, Sindirim, Dolaşım, Solunum, Üriner, Üreme)", "Komünite Ekolojisi", "Genden Proteine", "Canlılık ve Enerji", "Bitki Biyolojisi"],
    "TYT TÜRKÇE": ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Ses Bilgisi", "Yazım Kuralları", "Noktalama", "Sözcük Türleri", "Fiiller", "Cümlenin Ögeleri", "Anlatım Bozukluğu"],
    "AYT EDEBİYAT": ["Güzel Sanatlar ve Edebiyat", "Coşku ve Heyecanı Dile Getiren Metinler (Şiir)", "Olay Çevresinde Oluşan Metinler", "Öğretici Metinler", "Edebi Akımlar", "İslamiyet Öncesi Türk Edb.", "İslami Dönem Türk Edb.", "Divan Edebiyatı", "Halk Edebiyatı", "Tanzimat Edebiyatı", "Servet-i Fünun", "Fecr-i Ati", "Milli Edebiyat", "Cumhuriyet Dönemi"],
    "TYT TARİH": ["Tarih Bilimine Giriş", "İlk Çağ Uygarlıkları", "İslamiyet Öncesi Türk Tarihi", "İslam Tarihi", "Türk İslam Tarihi", "Osmanlı Devleti (Kuruluş-Yükselme)", "Osmanlı (Duraklama-Gerileme-Dağılma)", "Kurtuluş Savaşı Hazırlık", "Kurtuluş Savaşı Cepheler", "İnkılap Tarihi"],
    "AYT TARİH": ["Tarih Bilimi", "Uygarlığın Doğuşu", "İlk Türk Devletleri", "İslam Tarihi ve Uygarlığı", "Türk-İslam Devletleri", "Türkiye Tarihi", "Beylikten Devlete", "Dünya Gücü Osmanlı", "Arayış Yılları", "Diplomasi ve Değişim", "En Uzun Yüzyıl", "Milli Mücadele", "Atatürkçülük ve İnkılaplar", "İki Savaş Arasındaki Dönem", "II. Dünya Savaşı", "Soğuk Savaş Dönemi", "Küreselleşen Dünya"],
    "TYT COĞRAFYA": ["Doğa ve İnsan", "Dünya'nın Şekli ve Hareketleri", "Coğrafi Konum", "Harita Bilgisi", "İklim Bilgisi", "Yerin Şekillenmesi", "Nüfus ve Yerleşme", "Ulaşım Yolları", "Ekonomik Faaliyetler", "Bölgeler", "Doğal Afetler"],
    "AYT COĞRAFYA": ["Biyoçeşitlilik", "Ekosistem", "Nüfus Politikaları", "Türkiye'de Nüfus", "Türkiye'de Ekonomi", "Türkiye'de Tarım-Hayvancılık", "Türkiye'de Madenler-Sanayi", "Kültür Bölgeleri", "Küresel Ticaret", "Turizm", "Çevre Sorunları"],
    "FELSEFE GRUBU": ["Felsefeye Giriş", "Bilgi Felsefesi", "Varlık Felsefesi", "Ahlak Felsefesi", "Sanat Felsefesi", "Din Felsefesi", "Siyaset Felsefesi", "Bilim Felsefesi", "Psikoloji", "Sosyoloji", "Mantık"],
    "DİN KÜLTÜRÜ": ["Bilgi ve İnanç", "Din ve İslam", "İslam ve İbadet", "Gençlik ve Değerler", "Gönül Coğrafyamız", "Allah İnsan İlişkisi", "Hz. Muhammed", "Vahiy ve Akıl", "İslam Düşüncesinde Yorumlar"]
}

FLASHCARD_DERSLER = list(CIZELGE_DETAY.keys())

# --- FONKSİYONLAR ---
def make_hashes(p): return hashlib.sha256(str.encode(p)).hexdigest()

def init_files():
    if not os.path.exists(VIDEO_FOLDER): os.makedirs(VIDEO_FOLDER)
    if not os.path.exists(WORK_DATA) or os.stat(WORK_DATA).st_size == 0:
        pd.DataFrame(columns=["username", "Tarih", "Ders", "Konu", "Soru", "Süre"]).to_csv(WORK_DATA, index=False)
    
    files = [VIDEO_DATA, TASKS_DATA, BOOKS_DATA, GOALS_DATA, EMIR_QUESTIONS, SMART_FLASHCARD_DATA]
    for f in files:
        if not os.path.exists(f): pd.DataFrame().to_csv(f, index=False)

    if not os.path.exists(USER_DATA):
        df = pd.DataFrame(columns=["username", "password", "ad", "telefon", "email", "hedef", "is_coaching", "warnings", "plus"])
        admin_data = pd.DataFrame([[ADMIN_USER, make_hashes(ADMIN_PASS_RAW), "Emir Özkök", "05000000000", "admin@emir.com", "Mühendislik", "True", 0, "True"]], columns=df.columns)
        df = pd.concat([df, admin_data], ignore_index=True)
        df.to_csv(USER_DATA, index=False)
    else:
        # Admin şifresini güncelle ve is_coaching tipini sabitle
        try:
            ud = pd.read_csv(USER_DATA)
            if ADMIN_USER in ud['username'].values:
                ud.loc[ud['username'] == ADMIN_USER, 'password'] = make_hashes(ADMIN_PASS_RAW)
                ud.loc[ud['username'] == ADMIN_USER, 'is_coaching'] = "True"
                ud.to_csv(USER_DATA, index=False)
        except: pass

init_files()

# --- 🎨 CSS: RENKLİ & CANLI ---
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
    
    .login-box {
        background: #0f172a; padding: 40px; border-radius: 12px;
        border: 1px solid #1e293b; box-shadow: 0 10px 40px rgba(0,0,0,0.7); margin-top: 20px;
    }
    div.stTextInput > div > div > input, div.stSelectbox > div > button { background-color: #1e293b; color: white; border: 1px solid #334155; }
    div.stButton > button { background-color: transparent; color: white; border: 1px solid rgba(255,255,255,0.2); font-weight: bold; width: 100%; }

    .teams-link {
        display: block; width: 100%; padding: 15px;
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white !important; text-align: center; border-radius: 8px;
        text-decoration: none; font-weight: bold; font-size: 15px;
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
    st.markdown("<h1 style='text-align:center; font-size: 60px; color:#3b82f6; margin-bottom:20px;'>EMİR ÖZKÖK</h1>", unsafe_allow_html=True)
    st.markdown("""<div style='text-align:center; margin-bottom: 40px; padding: 0 5%;'><p style='color:#cbd5e1; font-size:18px; line-height:1.6;'>Sınav senesinde <b>"keşke böyle bir site olsaydı"</b> diyeceğim şekilde, ihtiyaçlarına göre bir site hazırladım. İçeride yaptıklarını kaydedebileceğin, ne kadar soru çözdüğünü anlık görebileceğin, önemli bilgileri not edip flash kartlarla çalışabileceğin bölümler ve daha nicesi...</p><p style='color:#3b82f6; font-weight:bold; font-size:20px; margin-top:15px;'>HADİ HEMEN KAYIT OL VE GİRİŞ YAP! 🚀</p></div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2], gap="large")
    with col1:
        found_files = glob.glob("emir_foto.*") + glob.glob("emir*.*")
        photo_path = None
        for f in found_files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jpg.jpg')): photo_path = f; break
        if photo_path:
            with open(photo_path, "rb") as image_file: encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'''<div style="width:100%; aspect-ratio: 1/1; overflow:hidden; border-radius:15px; border:2px solid #3b82f6; box-shadow: 0 0 30px rgba(59, 130, 246, 0.4);"><img src="data:image/png;base64,{encoded_string}" style="width:100%; height:100%; object-fit:cover;"></div>''', unsafe_allow_html=True)
        else: st.warning("Fotoğraf yok.")

    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 GİRİŞ YAP", "📝 KAYIT OL"])
        with tab1:
            u = st.text_input("Kullanıcı Adı", key="l_u")
            p = st.text_input("Şifre", type='password', key="l_p")
            if st.button("GİRİŞ YAP"):
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
                except: st.error("Sistem hazırlanıyor.")
        with tab2:
            n = st.text_input("Ad Soyad", key="r_n")
            ru = st.text_input("Kullanıcı Adı", key="r_u")
            rp = st.text_input("Şifre (Min 7 karakter)", type='password', key="r_p")
            rh = st.selectbox("Hedefin (Bölüm)", ["Sayısal", "Eşit Ağırlık", "Sözel", "Dil"], key="r_h")
            rt = st.text_input("Telefon", key="r_t", max_chars=11)
            rm = st.text_input("E-posta", key="r_m")
            if st.button("KAYDI TAMAMLA"):
                if not n or not ru or not rp: st.error("Boş alan bırakma.")
                else:
                    try:
                        ud = pd.read_csv(USER_DATA)
                        if ru not in ud['username'].values:
                            new_user = pd.DataFrame([[ru, make_hashes(rp), n, rt, rm, rh, "False", 0, "False"]], columns=ud.columns)
                            pd.concat([ud, new_user], ignore_index=True).to_csv(USER_DATA, index=False)
                            st.success("Kayıt Başarılı! Giriş yapabilirsiniz.")
                        else: st.error("Bu kullanıcı adı alınmış.")
                    except: st.error("Veritabanı hatası.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("""<a href="https://teams.live.com/l/community/FEA37u2Ksl3MjtjcgY" target="_blank" class="teams-link">🎁 Bedava hazır programlar ve taktikler için TOPLULUĞA KATIL</a>""", unsafe_allow_html=True)

# ==========================================
# 2. DASHBOARD
# ==========================================
elif st.session_state.logged_in and st.session_state.page == 'dashboard':
    
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
        df_w = pd.read_csv(WORK_DATA)
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
            st.markdown('<div class="dashboard-card card-orange"><h3>📊 ANALİZ</h3><p>Veri Girişi & İstatistik</p></div>', unsafe_allow_html=True)
            if st.button("İNCELE", use_container_width=True): go_to('stats')

        st.markdown("<br>", unsafe_allow_html=True)
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            st.markdown('<div class="dashboard-card card-dark"><h3>💬 SORU SOR</h3><p>Emir Hoca</p></div>', unsafe_allow_html=True)
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

    # --- ÖĞRENCİ LİSTESİ (HATA DÜZELTİLDİ: SÜTUN CONFIG) ---
    elif st.session_state.page == 'admin_users':
        st.header("👥 Öğrenci Yönetimi")
        st.info("❗ Koçluk yetkisi vermek için 'is_coaching' kutucuğunu işaretle ve KAYDET butonuna bas.")
        
        ud = pd.read_csv(USER_DATA)
        
        # 'is_coaching' sütununu boolean'a çevir (True/False)
        ud['is_coaching'] = ud['is_coaching'].apply(lambda x: str(x).lower() in ['true', '1', 'yes'])
        
        # Data editor ile checkbox göster
        edited_df = st.data_editor(
            ud, 
            num_rows="dynamic",
            column_config={
                "is_coaching": st.column_config.CheckboxColumn(
                    "Koçluk Öğrencisi mi?",
                    help="İşaretliyse öğrenciye ödev verebilirsin.",
                    default=False,
                )
            }
        )
        
        if st.button("💾 DEĞİŞİKLİKLERİ KAYDET"):
            # Kaydederken tekrar string 'True'/'False' yap
            edited_df['is_coaching'] = edited_df['is_coaching'].astype(str)
            edited_df.to_csv(USER_DATA, index=False)
            st.success("Veriler güncellendi!")
            time.sleep(1); st.rerun()

    elif st.session_state.page == 'stats':
        st.header("📊 Performans Analizi")
        with st.expander("📝 Manuel Veri Girişi", expanded=True):
            with st.form("manual_entry"):
                c_d1, c_d2 = st.columns(2)
                m_date = c_d1.date_input("Tarih Seç", date.today())
                m_ders = c_d2.selectbox("Ders Seç", list(CIZELGE_DETAY.keys()))
                c_d3, c_d4 = st.columns(2)
                m_soru = c_d3.number_input("Soru Sayısı", 0, 1000, 0)
                m_sure = c_d4.number_input("Süre (Dakika)", 0, 600, 0)
                if st.form_submit_button("LİSTEYE EKLE"):
                    try: df = pd.read_csv(WORK_DATA)
                    except: df = pd.DataFrame(columns=["username","Tarih","Ders","Konu","Soru","Süre"])
                    new_row = pd.DataFrame([[st.session_state.username, str(m_date), m_ders, "Bireysel", m_soru, m_sure]], columns=df.columns)
                    pd.concat([df, new_row], ignore_index=True).to_csv(WORK_DATA, index=False)
                    st.success("✅ Kaydedildi!")
                    time.sleep(1); st.rerun()
        try:
            df = pd.read_csv(WORK_DATA)
            my_data = df[df['username'] == st.session_state.username]
            if not my_data.empty:
                st.write("### 📈 Ders Dağılımı")
                st.bar_chart(my_data.groupby("Ders")["Soru"].sum())
                st.write("### 🗓️ Geçmiş")
                st.dataframe(my_data.sort_values(by="Tarih", ascending=False).head(10), use_container_width=True)
            else: st.info("Henüz veri yok.")
        except: st.error("Veri okuma hatası.")

    elif st.session_state.page == 'kronometre':
        st.header("⏱️ Odaklanma & Hedef")
        c_k1, c_k2 = st.columns([1, 1])
        with c_k1:
            st.subheader("🎯 Günlük Hedefin")
            try: 
                gd = pd.read_csv(GOALS_DATA)
                my_goal = gd[(gd['username']==st.session_state.username) & (gd['date']==str(date.today()))]
                target_val = my_goal.iloc[0]['target_min'] if not my_goal.empty else 0
            except: target_val = 0
            new_target = st.number_input("Bugün kaç dakika çalışacaksın?", value=int(target_val), step=10)
            if st.button("Hedefi Güncelle"):
                gd = pd.read_csv(GOALS_DATA) if os.path.exists(GOALS_DATA) else pd.DataFrame(columns=["username","date","target_min","status"])
                gd = gd[~((gd['username']==st.session_state.username) & (gd['date']==str(date.today())))]
                new_row = pd.DataFrame([[st.session_state.username, str(date.today()), new_target, "Set"]], columns=gd.columns)
                pd.concat([gd, new_row], ignore_index=True).to_csv(GOALS_DATA, index=False)
                st.success("Hedef belirlendi!")
        with c_k2:
            st.subheader("⏱️ Kronometre")
            t_ders = st.selectbox("Hangi derse çalışıyorsun?", list(CIZELGE_DETAY.keys()), key="timer_lesson")
            c_btn1, c_btn2, c_btn3 = st.columns(3)
            if c_btn1.button("▶️ BAŞLAT"):
                st.session_state.timer_active = True
                st.session_state.start_time = time.time()
                st.rerun()
            if c_btn2.button("⏸️ DURDUR"):
                st.session_state.elapsed_time += time.time() - st.session_state.start_time
                st.session_state.timer_active = False
                st.rerun()
            if c_btn3.button("💾 BİTİR VE KAYDET"):
                final_time = st.session_state.elapsed_time
                if st.session_state.timer_active: final_time += time.time() - st.session_state.start_time
                minutes = int(final_time / 60)
                if minutes > 0:
                    try: df = pd.read_csv(WORK_DATA)
                    except: df = pd.DataFrame(columns=["username","Tarih","Ders","Konu","Soru","Süre"])
                    new_row = pd.DataFrame([[st.session_state.username, str(date.today()), t_ders, "Kronometre", 0, minutes]], columns=df.columns)
                    pd.concat([df, new_row], ignore_index=True).to_csv(WORK_DATA, index=False)
                    st.success(f"{minutes} dakika kaydedildi!")
                st.session_state.elapsed_time = 0
                st.session_state.timer_active = False
                st.rerun()
            curr_time = st.session_state.elapsed_time
            if st.session_state.timer_active:
                curr_time += time.time() - st.session_state.start_time
                time.sleep(1); st.rerun()
            st.markdown(f"<h1 style='font-size: 60px; color: #3b82f6;'>{int(curr_time//60):02d}:{int(curr_time%60):02d}</h1>", unsafe_allow_html=True)

    # --- ÖDEV ATAMA PANELİ (DÜZELTİLDİ: KOÇLUK FİLTRESİ) ---
    elif st.session_state.page == 'admin_cizelge':
        st.header("Ödev Atama Merkezi")
        users = pd.read_csv(USER_DATA)
        
        # --- KRİTİK FİLTRE DÜZELTMESİ ---
        # Hem string 'True'/'true' hem de boolean True değerlerini kabul eder.
        st_list = users[
            (users['username'] != ADMIN_USER) & 
            (users['is_coaching'].apply(lambda x: str(x).strip().lower() in ['true', '1', 'yes']))
        ]['username'].tolist()
        
        if st_list:
            target = st.selectbox("Öğrenci Seç", st_list)
            st.write(f"### 📋 {target} - Ödev Geçmişi")
            try:
                td = pd.read_csv(TASKS_DATA)
                past_tasks = td[td['username'] == target][['tarih', 'ders', 'konu', 'gorev', 'durum']]
                st.dataframe(past_tasks.sort_values(by="tarih", ascending=False), use_container_width=True)
            except: st.write("Henüz ödev kaydı yok.")
            st.write("---")
            with st.expander("➕ Yeni Kitap Ekle"):
                bn = st.text_input("Kitap Adı")
                bc = st.selectbox("Ders", list(CIZELGE_DETAY.keys()))
                if st.button("Kitabı Ekle"):
                    bd = pd.read_csv(BOOKS_DATA)
                    pd.concat([bd, pd.DataFrame([[target, bn, bc, "Active"]], columns=bd.columns)]).to_csv(BOOKS_DATA, index=False)
                    st.success("Kitap eklendi!")
            st.subheader("📝 Yeni Ödev Ver")
            try: 
                bd = pd.read_csv(BOOKS_DATA)
                bks = bd[bd['username']==target]['book_name'].tolist()
            except: bks = []
            if bks:
                c1, c2, c3 = st.columns(3)
                s_kitap = c1.selectbox("Kitap", bks)
                s_ders = c2.selectbox("Ders", list(CIZELGE_DETAY.keys()))
                s_konu = c3.selectbox("Konu", CIZELGE_DETAY[s_ders])
                s_detay = st.text_input("Detay (Test No / Sayfa)")
                if st.button("ÖDEVİ GÖNDER", use_container_width=True):
                    td = pd.read_csv(TASKS_DATA)
                    new_task = pd.DataFrame([[int(time.time()), target, s_kitap, s_ders, s_konu, s_detay, "Yapılmadı", str(date.today())]], columns=td.columns)
                    pd.concat([td, new_task], ignore_index=True).to_csv(TASKS_DATA, index=False)
                    st.success("Ödev gönderildi!")
            else: st.warning("Önce kitap eklemelisin.")
        else: st.warning("Hiç koçluk öğrencisi yok veya filtre hatası. 'Öğrenci Listesi'nden yetki ver.")

    elif st.session_state.page == 'my_tasks':
        st.header("Ödevlerim")
        try: 
            td=pd.read_csv(TASKS_DATA)
            my=td[td['username']==st.session_state.username]
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
        st.header("Koçuna Sor")
        q = st.text_area("Mesajın")
        if st.button("Gönder"):
            try: Eq=pd.read_csv(EMIR_QUESTIONS)
            except: Eq=pd.DataFrame(columns=["id","Tarih","Kullanici","Soru","Durum"])
            pd.concat([Eq, pd.DataFrame([[int(time.time()), str(date.today()), st.session_state.username, q, "Sent"]], columns=Eq.columns)]).to_csv(EMIR_QUESTIONS, index=False); st.success("Mesaj iletildi")

    elif st.session_state.page == 'flashcards':
        st.header("Kartlar")
        t1, t2 = st.tabs(["Kart Ekle", "Çalış"])
        with t1:
            d = st.selectbox("Ders", FLASHCARD_DERSLER)
            q = st.text_input("Soru")
            a = st.text_input("Cevap")
            if st.button("Ekle"):
                fd = pd.read_csv(SMART_FLASHCARD_DATA)
                pd.concat([fd, pd.DataFrame([[st.session_state.username,d,q,a,str(date.today())]], columns=fd.columns)]).to_csv(SMART_FLASHCARD_DATA, index=False)
                st.success("Eklendi")
        with t2:
            try:
                fd = pd.read_csv(SMART_FLASHCARD_DATA)
                my = fd[fd['username']==st.session_state.username]
                if not my.empty:
                    if 'card_index' not in st.session_state: st.session_state.card_index = 0
                    if st.session_state.card_index >= len(my): st.session_state.card_index = 0
                    row = my.iloc[st.session_state.card_index]
                    st.markdown(f"<div class='dashboard-card'><h2>{row['soru']}</h2></div>", unsafe_allow_html=True)
                    if st.session_state.get('show_ans', False): st.success(f"Cevap: {row['cevap']}")
                    c1, c2 = st.columns(2)
                    if c1.button("Cevabı Gör"): st.session_state.show_ans = True; st.rerun()
                    if c2.button("Sıradaki"): 
                        st.session_state.card_index += 1
                        st.session_state.show_ans = False
                        st.rerun()
                else: st.warning("Henüz kart eklemedin.")
            except: st.error("Hata")

    elif st.session_state.page == 'admin_inbox':
        st.header("Gelen Kutusu")
        try: st.dataframe(pd.read_csv(EMIR_QUESTIONS))
        except: st.write("Mesaj yok")
    
    elif st.session_state.page == 'admin_books':
        st.header("Öğrenci Kitapları")
        try: st.dataframe(pd.read_csv(BOOKS_DATA))
        except: st.write("Kitap yok")

    elif st.session_state.page == 'admin_backup':
        st.header("💾 YEDEKLEME VE GERİ YÜKLEME MERKEZİ")
        st.warning("⚠️ Streamlit sunucusu yeniden başladığında veriler silinebilir. Buradan düzenli olarak dosyaları indir!")
        c_down, c_up = st.columns(2)
        with c_down:
            st.subheader("⬇️ 1. Verileri İndir (Yedekle)")
            files_to_download = [USER_DATA, TASKS_DATA, WORK_DATA, BOOKS_DATA, GOALS_DATA]
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
