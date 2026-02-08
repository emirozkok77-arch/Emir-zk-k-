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

# --- 📋 MÜFREDAT (EXCEL DOSYANDAKİ TAM LİSTE) ---
CIZELGE_DETAY = {
    "MATEMATİK (TYT-AYT)": [
        "Sayı Kümeleri (TYT)", "Sayı Basamakları (TYT)", "Asal Sayılar - Faktöriyel (TYT)", "Bölme - Bölünebilme (TYT)", 
        "EBOB - EKOK (TYT)", "Rasyonel Sayılar (TYT)", "1. Dereceden Denklemler (TYT)", "Basit Eşitsizlikler (TYT)", 
        "Mutlak Değer (TYT)", "Üslü Sayılar (TYT)", "Köklü Sayılar (TYT)", "Oran - Orantı (TYT)", "Sayı - Kesir Problemleri (TYT)", 
        "Yaş Problemleri (TYT)", "İşçi Problemleri (TYT)", "Hareket Problemleri (TYT)", "Yüzde - Kar - Zarar (TYT)", 
        "Karışım Problemleri (TYT)", "Grafik Problemleri (TYT)", "Sayısal Yetenek (TYT)", "Kümeler (TYT)", 
        "Mantık (TYT)", "Binom (TYT)", "Permütasyon - Kombinasyon (TYT)", "Olasılık (TYT)", "Polinomlar (TYT-AYT)", 
        "Fonksiyonlar (TYT-AYT)", "2. Dereceden Denklemler (AYT)", "Parabol (AYT)", "Eşitsizlikler (AYT)", 
        "Trigonometri (AYT)", "Logaritma (AYT)", "Diziler (AYT)", "Limit ve Süreklilik (AYT)", "Türev Alma Kuralları (AYT)", 
        "Türev Uygulamaları (AYT)", "İntegral (AYT)", "İntegral Alan Hesabı (AYT)"
    ],
    "GEOMETRİ (TYT-AYT)": [
        "Doğruda Açılar", "Üçgende Açılar", "Dik Üçgen", "İkizkenar Üçgen", "Eşkenar Üçgen", 
        "Açıortay", "Kenarortay", "Üçgende Alan", "Üçgende Benzerlik", "Açı-Kenar Bağıntıları", 
        "Çokgenler", "Dörtgenler", "Deltoid", "Paralelkenar", "Eşkenar Dörtgen", "Dikdörtgen", 
        "Kare", "Yamuk", "Çemberde Açı", "Çemberde Uzunluk", "Dairede Alan", 
        "Katı Cisimler (Prizma/Piramit)", "Noktanın Analitiği", "Doğrunun Analitiği", 
        "Dönüşüm Geometrisi", "Çember Analitiği"
    ],
    "FİZİK (TYT-AYT)": [
        "Fiziğin Doğası (TYT)", "Madde ve Özellikleri (TYT)", "Hareket ve Kuvvet (TYT)", 
        "İş - Güç - Enerji (TYT)", "Isı ve Sıcaklık (TYT)", "Elektrostatik (TYT)", "Elektrik Akımı (TYT)", 
        "Optik (TYT)", "Basınç ve Kaldırma (TYT)", "Dalgalar (TYT)", "Vektörler (AYT)", "Bağıl Hareket (AYT)", 
        "Newton Hareket Yasaları (AYT)", "Atışlar (AYT)", "İtme ve Momentum (AYT)", "Tork ve Denge (AYT)", 
        "Kütle Merkezi (AYT)", "Basit Makineler (AYT)", "Elektrik Alan ve Potansiyel (AYT)", 
        "Paralel Levhalar ve Sığa (AYT)", "Manyetizma (AYT)", "Alternatif Akım (AYT)", 
        "Çembersel Hareket (AYT)", "Basit Harmonik Hareket (AYT)", "Dalga Mekaniği (AYT)", 
        "Atom Fiziği (AYT)", "Modern Fizik (AYT)"
    ],
    "KİMYA (TYT-AYT)": [
        "Kimya Bilimi (TYT)", "Atom ve Periyodik Sistem (TYT)", "Kimyasal Türler Arası Etkileşim (TYT)", 
        "Maddenin Halleri (TYT)", "Kimyanın Temel Kanunları (TYT)", "Mol Kavramı (TYT)", 
        "Kimyasal Hesaplamalar (TYT)", "Karışımlar (TYT)", "Asitler - Bazlar - Tuzlar (TYT)", "Kimya Her Yerde (TYT)", 
        "Modern Atom Teorisi (AYT)", "Gazlar (AYT)", "Sıvı Çözeltiler (AYT)", "Kimyasal Tepkimelerde Enerji (AYT)", 
        "Kimyasal Hız (AYT)", "Kimyasal Denge (AYT)", "Asit - Baz Dengesi (AYT)", "Çözünürlük Dengesi (AYT)", 
        "Kimya ve Elektrik (AYT)", "Organik Kimya (AYT)"
    ],
    "BİYOLOJİ (TYT-AYT)": [
        "Canlıların Ortak Özellikleri (TYT)", "Temel Bileşenler (TYT)", "Hücre ve Organeller (TYT)", 
        "Madde Geçişleri (TYT)", "Sınıflandırma (TYT)", "Hücre Bölünmeleri (TYT)", "Kalıtım (TYT)", 
        "Ekosistem Ekolojisi (TYT)", "Sinir Sistemi (AYT)", "Endokrin Sistem (AYT)", "Duyu Organları (AYT)", 
        "Destek ve Hareket (AYT)", "Sindirim Sistemi (AYT)", "Dolaşım Sistemi (AYT)", "Solunum Sistemi (AYT)", 
        "Üriner Sistem (AYT)", "Üreme Sistemi (AYT)", "Komünite Ekolojisi (AYT)", "Protein Sentezi (AYT)", 
        "Canlılık ve Enerji (AYT)", "Bitki Biyolojisi (AYT)"
    ],
    "TÜRKÇE (TYT)": [
        "Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Ses Bilgisi", "Yazım Kuralları", 
        "Noktalama İşaretleri", "Sözcük Türleri", "Fiiller", "Cümlenin Ögeleri", 
        "Cümle Türleri", "Anlatım Bozukluğu"
    ]
}

HEDEFLER_LISTESI = ["Tıp", "Mühendislik", "Diş Hekimliği", "Hukuk", "Psikoloji", "Yazılım/Bilgisayar", "Mimarlık", "Pilotaj", "Eczacılık", "Diğer"]
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
        try:
            ud = pd.read_csv(USER_DATA)
            if ADMIN_USER in ud['username'].values:
                ud.loc[ud['username'] == ADMIN_USER, 'password'] = make_hashes(ADMIN_PASS_RAW)
                ud.to_csv(USER_DATA, index=False)
        except: pass

init_files()

# --- 🎨 CSS ---
st.markdown("""
<style>
    .stApp { background-color: #000000; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
    header, footer, #MainMenu, .stDeployButton, div[class^='viewerBadge'] {display: none !important;}
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }

    /* DASHBOARD KARTLARI */
    .dashboard-card {
        background-color: #0f172a; border: 1px solid #1e293b; border-radius: 12px;
        padding: 20px; height: 180px;
        display: flex; flex-direction: column; justify-content: space-between;
        transition: 0.3s;
    }
    .dashboard-card:hover { border-color: #3b82f6; box-shadow: 0 0 15px rgba(59, 130, 246, 0.2); }
    .card-title { font-size: 18px; font-weight: bold; color: #e2e8f0; display: flex; align-items: center; gap: 10px; }
    .card-desc { font-size: 13px; color: #94a3b8; margin-top: 5px; }

    /* NORMAL BUTONLAR (MAVİ ÇERÇEVELİ) */
    div.stButton > button {
        background-color: transparent; color: #3b82f6; border: 1px solid #3b82f6;
        width: 100%; font-weight: bold; border-radius: 8px; transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #3b82f6; color: white; }
    
    .login-box {
        background: #0f172a; padding: 40px; border-radius: 12px;
        border: 1px solid #1e293b; box-shadow: 0 10px 40px rgba(0,0,0,0.7); margin-top: 20px;
    }
    div.stTextInput > div > div > input, div.stSelectbox > div > button { background-color: #1e293b; color: white; border: 1px solid #334155; }
    
    /* TEAMS BUTONU (GRADIENT) */
    .teams-link {
        display: block; width: 100%; padding: 15px;
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white !important; text-align: center; border-radius: 8px;
        text-decoration: none; font-weight: bold; font-size: 15px;
        margin-top: 20px; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
        transition: 0.3s;
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
    
    # --- YENİ KARŞILAMA METNİ ---
    st.markdown("""
    <div style='text-align:center; margin-bottom: 40px; padding: 0 5%;'>
        <p style='color:#cbd5e1; font-size:18px; line-height:1.6;'>
        Sınav senesinde <b>"keşke böyle bir site olsaydı"</b> diyeceğim şekilde, ihtiyaçlarına göre bir site hazırladım.
        İçeride yaptıklarını kaydedebileceğin, o zamana kadar ne kadar soru çözdüğünü anlık görebileceğin,
        önemli bilgileri not edip flash kartlarla çalışabileceğin bölümler ve daha nicesi...
        </p>
        <p style='color:#3b82f6; font-weight:bold; font-size:20px; margin-top:15px;'>
        HADİ HEMEN KAYIT OL VE GİRİŞ YAP! 🚀
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2], gap="large")
    
    # --- SOL: FOTOĞRAF ---
    with col1:
        found_files = glob.glob("emir_foto.*") + glob.glob("emir*.*")
        photo_path = None
        for f in found_files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jpg.jpg')):
                photo_path = f; break
        
        if photo_path:
            with open(photo_path, "rb") as image_file: encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'''<div style="width:100%; aspect-ratio: 1/1; overflow:hidden; border-radius:15px; border:2px solid #3b82f6; box-shadow: 0 0 30px rgba(59, 130, 246, 0.3);"><img src="data:image/png;base64,{encoded_string}" style="width:100%; height:100%; object-fit:cover;"></div>''', unsafe_allow_html=True)
        else: st.warning("Fotoğraf yok. GitHub'a yükle.")

    # --- SAĞ: GİRİŞ & KAYIT ---
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 GİRİŞ YAP", "📝 KAYIT OL"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
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
                except: st.error("Sistem hazırlanıyor, tekrar dene.")
        
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            n = st.text_input("Ad Soyad", key="r_n")
            ru = st.text_input("Kullanıcı Adı", key="r_u")
            rp = st.text_input("Şifre (Min 7 karakter)", type='password', key="r_p")
            rh = st.selectbox("Hedefin (Bölüm)", HEDEFLER_LISTESI, key="r_h")
            rt = st.text_input("Telefon", key="r_t", max_chars=11)
            rm = st.text_input("E-posta", key="r_m")
            
            if st.button("KAYDI TAMAMLA"):
                if not n or not ru or not rp or not rt or not rm: st.error("Boş alan bırakma.")
                elif len(rp) < 7: st.error("Şifre kısa.")
                else:
                    try:
                        ud = pd.read_csv(USER_DATA)
                        if ru not in ud['username'].values:
                            new_user = pd.DataFrame([[ru, make_hashes(rp), n, rt, rm, rh, "False", 0, "False"]], columns=ud.columns)
                            pd.concat([ud, new_user], ignore_index=True).to_csv(USER_DATA, index=False)
                            st.success("Kayıt Başarılı! Giriş sekmesine geç.")
                        else: st.error("Bu kullanıcı adı alınmış.")
                    except: st.error("Veritabanı hatası.")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # --- TEAMS LİNKİ ---
        st.markdown("""
        <a href="https://teams.live.com/l/community/FEA37u2Ksl3MjtjcgY" target="_blank" class="teams-link">
        🎁 Bedava hazır programlar ve taktikler için TOPLULUĞA KATIL
        </a>
        """, unsafe_allow_html=True)

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

    # Çözülen soruyu hesapla
    try:
        df_w = pd.read_csv(WORK_DATA)
        total_solved = df_w[df_w['username'] == st.session_state.username]['Soru'].sum()
    except: total_solved = 0
    
    # YÖNETİCİ PANELİ
    if st.session_state.username == ADMIN_USER:
        st.info("🎓 YÖNETİCİ MODU")
        a1, a2, a3 = st.columns(3)
        with a1:
             st.markdown("<div class='dashboard-card'><div class='card-title'>👥 Öğrenciler</div><div class='card-desc'>Kayıtlı öğrencileri yönet</div></div>", unsafe_allow_html=True)
             if st.button("Öğrenci Listesi"): go_to('admin_users')
        with a2:
             st.markdown("<div class='dashboard-card'><div class='card-title'>📚 Ödev Ata</div><div class='card-desc'>Kitap ve görev ver</div></div>", unsafe_allow_html=True)
             if st.button("Ödev Paneli"): go_to('admin_cizelge')
        with a3:
             st.markdown("<div class='dashboard-card'><div class='card-title'>📩 Mesajlar</div><div class='card-desc'>Gelen sorular</div></div>", unsafe_allow_html=True)
             if st.button("Gelen Kutusu"): go_to('admin_inbox')
    
    st.write("")
    
    # GENEL MENÜ
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f"<div class='dashboard-card'><div class='card-title'>📢 Çözülen Soru</div><div class='card-desc' style='font-size:24px; color:white;'>{int(total_solved)}</div></div>", unsafe_allow_html=True)
    with r2:
        st.markdown("<div class='dashboard-card'><div class='card-title'>⏱️ Odaklanma</div><div class='card-desc'>Kronometre Başlat</div></div>", unsafe_allow_html=True)
        if st.button("BAŞLA", key="btn_odak"): go_to('kronometre')
    with r3:
        st.markdown("<div class='dashboard-card'><div class='card-title'>🎯 Günlük Hedef</div><div class='card-desc'>Süre Hedefi Koy</div></div>", unsafe_allow_html=True)
        if st.button("HEDEF KOY", key="btn_hedef"): go_to('goals')
        
    st.write("")
    
    r4, r5, r6 = st.columns(3)
    with r4:
        st.markdown("<div class='dashboard-card'><div class='card-title'>📚 Ödevlerim</div><div class='card-desc'>Sadece Koçluk Öğrencileri</div></div>", unsafe_allow_html=True)
        if st.session_state.get('is_coaching', False):
            if st.button("GÖREVLERİ AÇ"): go_to('my_tasks')
        else: st.button("🔒 KİLİTLİ", disabled=True)
    with r5:
        st.markdown("<div class='dashboard-card'><div class='card-title'>💬 Emir'e Sor</div><div class='card-desc'>Direkt İletişim</div></div>", unsafe_allow_html=True)
        if st.button("MESAJ GÖNDER"): go_to('ask_emir')
    with r6:
        st.markdown("<div class='dashboard-card'><div class='card-title'>🧠 Kartlar</div><div class='card-desc'>Akıllı Tekrar</div></div>", unsafe_allow_html=True)
        if st.button("ÇALIŞ"): go_to('flashcards')
    
    st.write("")
    if st.button("📊 DETAYLI İSTATİSTİK VE ANALİZ"): go_to('stats')

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
        st.header("📊 PERFORMANS VE ANALİZ")
        try:
            df = pd.read_csv(WORK_DATA)
            if df.empty:
                st.info("Henüz çalışma verisi yok.")
            else:
                my_data = df[df['username'] == st.session_state.username]
                total = my_data['Soru'].sum() if not my_data.empty else 0
                
                c1, c2 = st.columns(2)
                c1.metric("Toplam Çözülen Soru", int(total))
                c2.metric("Toplam Çalışma", f"{int(my_data['Süre'].sum() if not my_data.empty else 0)} dk")
                
                st.markdown("---")
                t1, t2 = st.tabs(["DERS DAĞILIMI", "LİDERLİK"])
                with t1:
                    if not my_data.empty: st.bar_chart(my_data.groupby("Ders")["Soru"].sum())
                    else: st.info("Veri yok.")
                with t2:
                    real = df.groupby("username")[["Soru", "Süre"]].sum().reset_index()
                    st.dataframe(real.sort_values(by="Soru", ascending=False), use_container_width=True)
        except Exception as e:
            st.warning("Veritabanı hazırlanıyor, lütfen bir çalışma kaydedip tekrar deneyin.")
            pd.DataFrame(columns=["username","Tarih","Ders","Konu","Soru","Süre"]).to_csv(WORK_DATA, index=False)

    elif st.session_state.page == 'kronometre':
        st.header("⏱️ ODAKLANMA")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("BAŞLAT"): st.session_state.timer_active=True; st.session_state.start_time=time.time(); st.rerun()
            if st.button("DURAKLAT"): st.session_state.elapsed_time+=time.time()-st.session_state.start_time; st.session_state.timer_active=False; st.rerun()
            if st.button("KAYDET"):
                m = int(st.session_state.elapsed_time/60)
                if m>0:
                    try: df = pd.read_csv(WORK_DATA)
                    except: df = pd.DataFrame(columns=["username","Tarih","Ders","Konu","Soru","Süre"])
                    new_row = pd.DataFrame([[st.session_state.username,str(date.today()),"Genel","Kronometre",0,m]], columns=df.columns)
                    pd.concat([df, new_row], ignore_index=True).to_csv(WORK_DATA, index=False)
                    st.success("Kaydedildi!")
                st.session_state.elapsed_time=0; st.session_state.timer_active=False; st.rerun()
        with c2:
            t = st.session_state.elapsed_time + (time.time()-st.session_state.start_time if st.session_state.timer_active else 0)
            st.markdown(f"<h1 style='font-size:80px; color:#3b82f6;'>{int(t//60):02d}:{int(t%60):02d}</h1>", unsafe_allow_html=True)
            if st.session_state.timer_active: time.sleep(1); st.rerun()

    elif st.session_state.page == 'admin_cizelge':
        st.header("Ödev Paneli")
        users = pd.read_csv(USER_DATA)
        st_list = users[(users['username']!=ADMIN_USER) & (users['is_coaching']==True)]['username'].tolist()
        
        if st_list:
            target = st.selectbox("Öğrenci", st_list)
            
            with st.expander("➕ Yeni Kitap Ekle", expanded=False):
                c_kb1, c_kb2 = st.columns(2)
                bn = c_kb1.text_input("Kitap Adı (Örn: 345 TYT Mat)")
                bc = c_kb2.selectbox("Ders", list(CIZELGE_DETAY.keys()))
                if st.button("Kitabı Ekle"):
                    try: bd=pd.read_csv(BOOKS_DATA)
                    except: bd=pd.DataFrame(columns=["username","book_name","category","status"])
                    pd.concat([bd, pd.DataFrame([[target, bn, bc, "Active"]], columns=bd.columns)]).to_csv(BOOKS_DATA, index=False); st.success("Kitap Eklendi")
            
            st.write("---")
            st.subheader("📚 Ödev Atama")
            
            try: 
                bd=pd.read_csv(BOOKS_DATA)
                bks=bd[bd['username']==target]['book_name'].tolist()
            except: bks=[]
            
            if bks:
                col_sel1, col_sel2, col_sel3 = st.columns(3)
                secilen_kitap = col_sel1.selectbox("Hangi Kitaptan?", bks)
                secilen_ders = col_sel2.selectbox("Ders Seç", list(CIZELGE_DETAY.keys()))
                konular = CIZELGE_DETAY[secilen_ders]
                secilen_konu = col_sel3.selectbox("Konu Seç", konular)
                test_no = st.text_input("Test No / Sayfa Aralığı (Örn: Test 3, 4, 5)")
                
                if st.button("ÖDEVİ GÖNDER", use_container_width=True):
                    try: td=pd.read_csv(TASKS_DATA)
                    except: td=pd.DataFrame(columns=["id","username","book","ders","konu","gorev","durum","tarih"])
                    gorev_metni = f"{test_no}"
                    new_task = pd.DataFrame([[int(time.time()), target, secilen_kitap, secilen_ders, secilen_konu, gorev_metni, "Yapılmadı", str(date.today())]], columns=td.columns)
                    pd.concat([td, new_task], ignore_index=True).to_csv(TASKS_DATA, index=False)
                    st.success(f"✅ {target} kişisine '{secilen_konu}' konusu ödev verildi!")
            else:
                st.warning("Öğrencinin kayıtlı kitabı yok. Önce yukarıdan kitap ekle.")
        else: st.warning("Koçluk öğrencisi yok.")

    elif st.session_state.page == 'my_tasks':
        st.header("Ödevlerim")
        try: 
            td=pd.read_csv(TASKS_DATA)
            my=td[td['username']==st.session_state.username]
            if my.empty:
                st.info("Harika! Yapılacak ödevin yok.")
            else:
                my = my.sort_values(by="durum", ascending=False)
                for i, r in my.iterrows():
                    container = st.container()
                    if r['durum'] == 'Yapılmadı':
                        container.error(f"📌 {r['ders']} | {r['konu']}")
                        c1, c2, c3 = container.columns([2, 4, 1])
                        c1.write(f"**{r['book']}**")
                        c2.write(f"Görev: {r['gorev']}")
                        if c3.button("BİTİR", key=f"d{r['id']}"):
                            td.loc[td['id']==r['id'], 'durum'] = 'Tamamlandı'
                            td.to_csv(TASKS_DATA, index=False)
                            st.rerun()
                    else:
                        with container.expander(f"✅ {r['ders']} - {r['konu']} (Tamamlandı)"):
                            st.write(f"Kitap: {r['book']}")
                            st.write(f"Detay: {r['gorev']}")
                            st.caption(f"Tarih: {r['tarih']}")
        except: st.info("Ödev sistemi hazırlanıyor.")

    elif st.session_state.page == 'goals':
        st.header("Hedef")
        st.write("Hedeflerini buradan takip et.")
    
    elif st.session_state.page == 'ask_emir':
        st.header("Koçuna Sor")
        q = st.text_area("Mesajın")
        if st.button("Gönder"):
            try: Eq=pd.read_csv(EMIR_QUESTIONS)
            except: Eq=pd.DataFrame(columns=["id","Tarih","Kullanici","Soru","Durum"])
            pd.concat([Eq, pd.DataFrame([[int(time.time()), str(date.today()), st.session_state.username, q, "Sent"]], columns=Eq.columns)]).to_csv(EMIR_QUESTIONS, index=False); st.success("Mesaj iletildi")

    elif st.session_state.page == 'flashcards':
        st.header("Kartlar")
        t1, t2 = st.tabs(["Ekle", "Çalış"])
        with t1:
            d = st.selectbox("Ders", FLASHCARD_DERSLER); q=st.text_input("Soru"); a=st.text_input("Cevap")
            if st.button("Ekle"):
                try: fd=pd.read_csv(SMART_FLASHCARD_DATA)
                except: fd=pd.DataFrame(columns=["username","ders","soru","cevap","tarih"])
                pd.concat([fd, pd.DataFrame([[st.session_state.username,d,q,a,str(date.today())]], columns=fd.columns)]).to_csv(SMART_FLASHCARD_DATA,index=False); st.success("OK")
        with t2:
            try: 
                fd=pd.read_csv(SMART_FLASHCARD_DATA); my=fd[fd['username']==st.session_state.username]
                if not my.empty:
                    if st.session_state.card_index >= len(my): st.session_state.card_index=0
                    row = my.iloc[st.session_state.card_index]
                    st.markdown(f"<div class='dashboard-card'><h2>{row['soru']}</h2></div>", unsafe_allow_html=True)
                    if st.session_state.show_answer: st.success(row['cevap'])
                    c_a, c_b = st.columns(2)
                    if c_a.button("Cevap"): st.session_state.show_answer=not st.session_state.show_answer; st.rerun()
                    if c_b.button("Sıradaki"): st.session_state.card_index+=1; st.session_state.show_answer=False; st.rerun()
            except: st.write("Kart yok")
    
    elif st.session_state.page == 'admin_inbox':
        st.header("Gelen Kutusu")
        try: st.dataframe(pd.read_csv(EMIR_QUESTIONS))
        except: st.write("Mesaj yok")
    
    elif st.session_state.page == 'admin_books':
        st.header("Öğrenci Kitapları")
        try: st.dataframe(pd.read_csv(BOOKS_DATA))
        except: st.write("Kitap yok")
