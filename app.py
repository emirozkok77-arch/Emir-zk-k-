import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, date, timedelta
import time
import requests
import json
import random
import glob
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Emir Özkök Akademi", layout="wide", page_icon="🧿", initial_sidebar_state="collapsed")

# --- 🏛️ DOSYALAR ---
USER_DATA = "users.csv"; WORK_DATA = "calisma_verileri.csv"; VIDEO_DATA = "videolar.csv"
TASKS_DATA = "odevler.csv"; BOOKS_DATA = "ogrenci_kitaplari.csv"; GOALS_DATA = "hedefler.csv"
EMIR_QUESTIONS = "emire_gelen_sorular.csv"; SMART_FLASHCARD_DATA = "akilli_kartlar.csv"
VIDEO_FOLDER = "ozel_videolar"; ADMIN_USER = "emirozkok"

# --- 📋 MÜFREDAT ---
CIZELGE_DETAY = {
    "FİZİK (TYT-AYT)": ["Fiziğin Doğası", "Vektör-Kuvvet", "Hareket", "Dinamik", "İş-Güç-Enerji", "Elektrik", "Manyetizma", "Dalgalar", "Optik", "Modern Fizik"],
    "KİMYA (TYT-AYT)": ["Kimya Bilimi", "Atom", "Periyodik Cetvel", "Türler Arası Etkileşim", "Mol", "Tepkimeler", "Çözeltiler", "Gazlar", "Hız-Denge", "Organik"],
    "BİYOLOJİ (TYT-AYT)": ["Canlıların Ortak Özellikleri", "Hücre", "Sınıflandırma", "Bölünmeler", "Kalıtım", "Ekoloji", "Sistemler", "Bitki Biyolojisi"],
    "MATEMATİK (TYT-AYT)": ["Temel Kavramlar", "Problemler", "Fonksiyonlar", "Polinom", "2.Dereceden Denklem", "Trigonometri", "Logaritma", "Diziler", "Limit", "Türev", "İntegral"],
    "GEOMETRİ": ["Üçgenler", "Çokgenler", "Dörtgenler", "Çember-Daire", "Analitik", "Katı Cisimler"]
}
FLASHCARD_DERSLER = ["TYT Matematik", "AYT Matematik", "Geometri", "TYT Fizik", "AYT Fizik", "TYT Kimya", "AYT Kimya", "TYT Biyoloji", "AYT Biyoloji", "TYT Türkçe", "AYT Edebiyat", "Tarih", "Coğrafya"]

# --- FONKSİYONLAR ---
def make_hashes(p): return hashlib.sha256(str.encode(p)).hexdigest()

def init_files():
    if not os.path.exists(VIDEO_FOLDER): os.makedirs(VIDEO_FOLDER)
    files = [USER_DATA, WORK_DATA, VIDEO_DATA, TASKS_DATA, BOOKS_DATA, GOALS_DATA, EMIR_QUESTIONS, SMART_FLASHCARD_DATA]
    if not os.path.exists(USER_DATA):
        pd.DataFrame(columns=["username", "password", "ad", "telefon", "email", "hedef", "is_coaching", "warnings", "plus"]).to_csv(USER_DATA, index=False)
        ud = pd.read_csv(USER_DATA)
        if ADMIN_USER not in ud['username'].values:
            pd.concat([ud, pd.DataFrame([[ADMIN_USER, make_hashes("123"), "Emir Özkök", "05000000000", "admin@emir.com", "Boğaziçi", "True", 0, "True"]], columns=ud.columns)]).to_csv(USER_DATA, index=False)
    for f in files:
        if not os.path.exists(f) and f != USER_DATA: pd.DataFrame().to_csv(f, index=False)

init_files()

# --- 🎨 CSS: NÜKLEER REKLAM ENGELLEYİCİ (V330) ---
st.markdown("""
<style>
    /* GENEL */
    .stApp { background-color: #02040a; color: #e2e8f0; font-family: 'Inter', sans-serif; }
    
    /* --- ZORLA GİZLEME KODLARI --- */
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important; height: 0px !important;}
    #MainMenu {visibility: hidden !important;}
    .stDeployButton {display:none !important;}
    .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
    div[class^='viewerBadge'] { display: none !important; }
    iframe[title="streamlitApp"] { bottom: 0 !important; }

    /* --- DASHBOARD KARTLARI (RENKLİ) --- */
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

    /* RENKLER */
    .card-purple { background: linear-gradient(135deg, #9b5de5, #f15bb5); }
    .card-mustard { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); }
    .card-orange { background: linear-gradient(135deg, #ff9966, #ff5e62); }
    .card-blue { background: linear-gradient(135deg, #00c6ff, #0072ff); }
    .card-dark { background: linear-gradient(135deg, #434343, #000000); }
    
    /* --- GİRİŞ SAYFASI --- */
    .login-box {
        background: #0f172a; padding: 40px; border-radius: 12px;
        border: 1px solid #1e293b; box-shadow: 0 10px 40px rgba(0,0,0,0.7);
        margin-top: 20px;
    }
    .square-img {
        width: 100%; aspect-ratio: 1 / 1; object-fit: cover;
        border-radius: 15px; border: 2px solid #3b82f6;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
    }
    .highlight-box {
        background: rgba(59, 130, 246, 0.1);
        border-left: 5px solid #3b82f6; padding: 20px;
        border-radius: 0 10px 10px 0; margin: 20px 0;
    }
    .teams-btn {
        display: block; width: 100%; padding: 20px;
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white !important; text-align: center; border-radius: 8px;
        text-decoration: none; font-weight: bold; font-size: 20px;
        border: 1px solid #60a5fa; transition: 0.3s;
    }
    .teams-btn:hover { transform: scale(1.02); }
    
    div.stTextInput > div > div > input { background-color: #1e293b; color: white; border: 1px solid #334155; }
    div.stButton > button { background-color: transparent; color: white; border: 1px solid rgba(255,255,255,0.2); font-weight: bold; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- SESSION ---
if 'page' not in st.session_state: st.session_state.page = 'landing'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'timer_active' not in st.session_state: st.session_state.timer_active = False
if 'elapsed_time' not in st.session_state: st.session_state.elapsed_time = 0
if 'start_time' not in st.session_state: st.session_state.start_time = 0
if 'last_request_time' not in st.session_state: st.session_state.last_request_time = 0

def go_to(page): st.session_state.page = page; st.rerun()

# ==========================================
# 1. LANDING PAGE
# ==========================================
if st.session_state.page == 'landing' and not st.session_state.logged_in:
    
    st.markdown("<h1 style='text-align:center; font-size: 70px; margin:0; color:#3b82f6;'>EMİR ÖZKÖK</h1>", unsafe_allow_html=True)
    # --- YAZI BURADAN SİLİNDİ ---
    st.markdown("---")

    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        found_files = glob.glob("emir_foto.*") + glob.glob("emir*.*")
        photo_path = None
        for f in found_files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jpg.jpg')):
                photo_path = f; break
        
        if photo_path:
            with open(photo_path, "rb") as image_file: encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'''<div style="width:100%; aspect-ratio: 1/1; overflow:hidden; border-radius:15px; border:2px solid #3b82f6;"><img src="data:image/png;base64,{encoded_string}" style="width:100%; height:100%; object-fit:cover;"></div>''', unsafe_allow_html=True)
        else: st.warning("Fotoğraf yok."); st.file_uploader("Yükle", type=['jpg'])

    with col2:
        st.markdown("<h2 style='color:#3b82f6; margin-top:0;'>BEN EMİR ÖZKÖK.</h2>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#cbd5e1; font-weight:normal;'>BOĞAZİÇİ ÜNİVERSİTESİ <br> MAKİNE MÜHENDİSLİĞİ</h3>", unsafe_allow_html=True)
        st.markdown("""
        <p style='font-size:18px; line-height:1.6; color:#94a3b8;'>
        Sınav senemde yaşadığım en büyük sorun <b>"bilgi kirliliği"</b> ve <b>"strateji eksikliği"</b> idi. 
        Herkes çalışıyordu ama kimse stratejik çalışmıyordu.
        </p>
        <div class="highlight-box">
            <span style='font-size:24px; font-weight:bold; color:#e2e8f0;'>
            SINAV SÜRECİNDEKİ ÇEKTİĞİM SORUNLARI <br> 
            <span style='color:#3b82f6;'>SİZLER İÇİN ÇÖZDÜM.</span>
            </span>
        </div>
        <p style='font-size:16px; font-style:italic; color:#64748b;'>
        "Burası sadece bir site değil, başarıya giden stratejik karargahınız."
        </p>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    c_team1, c_team2, c_team3 = st.columns([1, 4, 1])
    with c_team2:
        st.markdown("<h4 style='text-align:center; color:#e2e8f0; margin-bottom:10px;'>İÇERİDEKİ YERİNİ AL</h4>", unsafe_allow_html=True)
        st.markdown("""<a href="https://teams.live.com/l/community/FEA37u2Ksl3MjtjcgY" class="teams-btn" target="_blank">🚀 MICROSOFT TEAMS TOPLULUĞUNA KATIL</a>""", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#64748b; font-size:14px; margin-top:5px;'>*Ücretsiz programlar ve özel kanallar.</p>", unsafe_allow_html=True)

    st.markdown("<br><hr style='border-color:#334155;'><br>", unsafe_allow_html=True)

    c_auth1, c_auth2, c_auth3 = st.columns([1, 2, 1])
    with c_auth2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 GİRİŞ YAP", "📝 KAYIT OL"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            u = st.text_input("Kullanıcı Adı", key="l_u")
            p = st.text_input("Şifre", type='password', key="l_p")
            if st.button("GİRİŞ"):
                time.sleep(0.5)
                ud = pd.read_csv(USER_DATA); hp = make_hashes(p)
                user = ud[(ud['username']==u) & (ud['password']==hp)]
                if not user.empty:
                    st.session_state.logged_in=True; st.session_state.username=u; st.session_state.realname=user.iloc[0]['ad']
                    st.session_state.is_coaching = (str(user.iloc[0]['is_coaching']) == "True" or u == ADMIN_USER)
                    st.session_state.page='dashboard'; st.rerun()
                else: st.error("Hatalı bilgiler.")
        
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.warning("⚠️ Tüm alanlar zorunludur.")
            n = st.text_input("Ad Soyad", key="r_n")
            ru = st.text_input("Kullanıcı Adı", key="r_u")
            rp = st.text_input("Şifre (En az 7 karakter)", type='password', key="r_p")
            c1, c2 = st.columns(2)
            with c1: rt = st.text_input("Telefon (Rakam)", key="r_t", max_chars=11)
            with c2: rm = st.text_input("E-posta", key="r_m")
            
            if st.button("KAYDI TAMAMLA"):
                if time.time() - st.session_state.last_request_time < 2: st.error("Çok hızlı işlem. Bekle.")
                else:
                    st.session_state.last_request_time = time.time()
                    if not n or not ru or not rp or not rt or not rm: st.error("Boş alan bırakma.")
                    elif len(rp) < 7: st.error("Şifre kısa.")
                    elif not rt.isdigit(): st.error("Telefon sadece rakam.")
                    elif "@" not in rm or "." not in rm: st.error("Geçersiz mail.")
                    else:
                        ud=pd.read_csv(USER_DATA)
                        if ru not in ud['username'].values:
                            pd.concat([ud,pd.DataFrame([[ru,make_hashes(rp),n,rt,rm,"Boğaziçi","False",0,"False"]],columns=ud.columns)],ignore_index=True).to_csv(USER_DATA,index=False)
                            st.success("Kayıt Başarılı!"); time.sleep(1)
                        else: st.error("Kullanıcı adı alınmış.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# 2. DASHBOARD
# ==========================================
elif st.session_state.logged_in and st.session_state.page == 'dashboard':
    
    c_head, c_btn = st.columns([9, 1])
    with c_head: st.markdown(f"## 👋 {st.session_state.realname}")
    with c_btn: 
        if st.button("ÇIKIŞ"): st.session_state.logged_in=False; st.rerun()
    st.markdown("---")

    try:
        df_w = pd.read_csv(WORK_DATA)
        total_solved = df_w[df_w['username'] == st.session_state.username]['Soru'].sum()
    except: total_solved = 0

    cL, cR = st.columns([1, 2])
    
    with cL:
        st.markdown(f"""
        <div class='dashboard-card card-blue' style='height: auto; align-items: flex-start; text-align: left; background: #1e293b; border: 1px solid #3b82f6;'>
            <h3 style='color:#3b82f6;'>📊 DURUM RAPORU</h3>
            <p style='font-size:30px; font-weight:bold; color:white;'>{int(total_solved)} <span style='font-size:16px; font-weight:normal; color:#aaa;'>Soru Çözüldü</span></p>
        </div>
        <div style='height:20px;'></div>
        <div class='dashboard-card card-blue' style='height: auto; align-items: flex-start; text-align: left;'>
            <h3>📢 GÜNCEL AKIŞ</h3>
            <p>Karargah Bildirimleri</p>
            <hr style='width:100%; border-color:rgba(255,255,255,0.3);'>
        """, unsafe_allow_html=True)
        if os.path.exists(VIDEO_DATA):
            try:
                vids = pd.read_csv(VIDEO_DATA).iloc[::-1].head(3)
                for _, r in vids.iterrows():
                    st.write(f"**{r['baslik']}**")
                    if os.path.exists(r['dosya_yolu']): st.video(r['dosya_yolu'])
            except: st.write("Video yok.")
        st.markdown("</div>", unsafe_allow_html=True)
    
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
            st.markdown('<div class="dashboard-card card-mustard"><h3>⏱️ ODAK</h3><p>Kronometre</p></div>', unsafe_allow_html=True)
            if st.button("BAŞLA", use_container_width=True): go_to('kronometre')
            
        with r1_c3:
            st.markdown('<div class="dashboard-card card-orange"><h3>📊 ANALİZ</h3><p>İstatistikler</p></div>', unsafe_allow_html=True)
            if st.button("İNCELE", use_container_width=True): go_to('stats')

        st.markdown("<br>", unsafe_allow_html=True)

        r2_c1, r2_c2, r2_c3 = st.columns(3)
        with r2_c1:
            st.markdown('<div class="dashboard-card card-blue"><h3>🎯 HEDEF</h3><p>Günlük Plan</p></div>', unsafe_allow_html=True)
            if st.button("HEDEF KOY", use_container_width=True): go_to('goals')
            
        with r2_c2:
            st.markdown('<div class="dashboard-card card-dark"><h3>💬 SORU SOR</h3><p>Emir Hoca</p></div>', unsafe_allow_html=True)
            if st.button("MESAJ AT", use_container_width=True): go_to('ask_emir')

        with r2_c3:
            st.markdown('<div class="dashboard-card card-purple" style="background: linear-gradient(135deg, #E91E63, #9C27B0);"><h3>🧠 KARTLAR</h3><p>Flashcards</p></div>', unsafe_allow_html=True)
            if st.button("ÇALIŞ", use_container_width=True): go_to('flashcards')

        if st.session_state.username == ADMIN_USER:
            st.markdown("---")
            a1, a2, a3 = st.columns(3)
            with a1: 
                if st.button("KİTAPLARI YÖNET"): go_to('admin_books')
            with a2: 
                if st.button("ÖĞRENCİ YETKİ"): go_to('admin_users')
            with a3: 
                if st.button("GELEN MESAJLAR"): go_to('admin_inbox')

# ==========================================
# 3. İÇ SAYFALAR
# ==========================================
elif st.session_state.logged_in:
    c_back, c_tit = st.columns([1, 10])
    with c_back: 
        if st.button("⬅️", key="nav_back"): go_to('dashboard')
    
    if st.session_state.page == 'stats':
        st.header("📊 PERFORMANS VE ANALİZ")
        df = pd.read_csv(WORK_DATA)
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
            fake = pd.DataFrame([["Emir Özkök (BOSS)", 85432, 99999]], columns=["username", "Soru", "Süre"])
            st.dataframe(pd.concat([fake, real]).sort_values(by="Soru", ascending=False), use_container_width=True)

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
            with st.expander("Kitap Ekle"):
                bn = st.text_input("Kitap Adı"); bc = st.selectbox("Ders", list(CIZELGE_DETAY.keys()))
                if st.button("Ekle"):
                    try: bd=pd.read_csv(BOOKS_DATA)
                    except: bd=pd.DataFrame(columns=["username","book_name","category","status"])
                    pd.concat([bd, pd.DataFrame([[target, bn, bc, "Active"]], columns=bd.columns)]).to_csv(BOOKS_DATA, index=False); st.success("OK")
            try: bd=pd.read_csv(BOOKS_DATA); bks=bd[bd['username']==target]['book_name'].tolist()
            except: bks=[]
            if bks:
                bk = st.selectbox("Kitap", bks)
                c1, c2, c3 = st.columns(3)
                for i, (d, k) in enumerate(CIZELGE_DETAY.items()):
                    with [c1,c2,c3][i%3]:
                        st.write(f"**{d}**")
                        for sub in k:
                            if st.button(f"+ {sub}", key=f"{d}{sub}"):
                                try: td=pd.read_csv(TASKS_DATA)
                                except: td=pd.DataFrame(columns=["id","username","book","ders","konu","gorev","durum","tarih"])
                                pd.concat([td, pd.DataFrame([[int(time.time()),target,bk,d,sub,"Yap","Yapılmadı",str(date.today())]], columns=td.columns)]).to_csv(TASKS_DATA, index=False); st.success("Verildi")
            else: st.warning("Önce kitap ekle.")
        else: st.warning("Koçluk öğrencisi yok.")

    elif st.session_state.page == 'my_tasks':
        st.header("Ödevlerim")
        try: 
            td=pd.read_csv(TASKS_DATA); my=td[td['username']==st.session_state.username]
            for i, r in my.iterrows():
                c1, c2 = st.columns([4,1])
                c1.info(f"{r['ders']} - {r['konu']} ({r['book']})")
                if r['durum'] == 'Yapılmadı':
                    if c2.button("BİTİR", key=f"d{r['id']}"):
                        td.at[i,'durum']='Tamamlandı'; td.to_csv(TASKS_DATA,index=False); st.rerun()
        except: st.info("Ödev yok.")

    elif st.session_state.page == 'goals':
        st.header("Hedef")
        m = st.number_input("Dakika Hedefi", 0, 1000)
        if st.button("Kaydet"):
            try: Gd=pd.read_csv(GOALS_DATA)
            except: Gd=pd.DataFrame(columns=["username","date","target_min","status"])
            pd.concat([Gd, pd.DataFrame([[st.session_state.username, str(date.today()), m, "Pending"]], columns=Gd.columns)]).to_csv(GOALS_DATA, index=False); st.success("OK")

    elif st.session_state.page == 'ask_emir':
        q = st.text_area("Mesaj")
        if st.button("Gönder"):
            try: Eq=pd.read_csv(EMIR_QUESTIONS)
            except: Eq=pd.DataFrame(columns=["id","Tarih","Kullanici","Soru","Durum"])
            pd.concat([Eq, pd.DataFrame([[int(time.time()), str(date.today()), st.session_state.username, q, "Sent"]], columns=Eq.columns)]).to_csv(EMIR_QUESTIONS, index=False); st.success("Gitti")
            
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

    elif st.session_state.page == 'admin_users':
        ud = pd.read_csv(USER_DATA)
        edited = st.data_editor(ud)
        if st.button("Kaydet"): edited.to_csv(USER_DATA, index=False); st.success("OK")
    
    elif st.session_state.page == 'admin_inbox':
        try: st.dataframe(pd.read_csv(EMIR_QUESTIONS))
        except: st.write("Mesaj yok")
    
    elif st.session_state.page == 'admin_books':
        try: st.dataframe(pd.read_csv(BOOKS_DATA))
        except: st.write("Kitap yok")
