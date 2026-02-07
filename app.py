import streamlit as st
import pandas as pd
import os
import hashlib
import time
import base64
import glob
from datetime import date

# --- 1. AYARLAR (En Başta Olmalı) ---
st.set_page_config(page_title="Emir Akademi", layout="wide", page_icon="🧿", initial_sidebar_state="collapsed")

# --- HATA YAKALAYICI (DEBUG) ---
try:
    # --- 2. DOSYALAR VE SABİTLER ---
    USER_DATA = "users.csv"
    WORK_DATA = "calisma_verileri.csv"
    VIDEO_DATA = "videolar.csv"
    TASKS_DATA = "odevler.csv"
    BOOKS_DATA = "ogrenci_kitaplari.csv"
    GOALS_DATA = "hedefler.csv"
    EMIR_QUESTIONS = "emire_gelen_sorular.csv"
    SMART_FLASHCARD_DATA = "akilli_kartlar.csv"
    VIDEO_FOLDER = "ozel_videolar"
    ADMIN_USER = "emirozkok"
    
    HEDEFLER_LISTESI = ["Tıp", "Mühendislik", "Diş Hekimliği", "Hukuk", "Psikoloji", "Yazılım", "Mimarlık", "Diğer"]
    FLASHCARD_DERSLER = ["Matematik", "Fizik", "Kimya", "Biyoloji", "Türkçe", "Tarih", "Coğrafya"]
    CIZELGE_DETAY = {"MATEMATİK": ["Temel Kavramlar", "Problemler", "Fonksiyonlar"], "FİZİK": ["Kuvvet", "Hareket", "Elektrik"]}

    # --- 3. FONKSİYONLAR ---
    def make_hashes(p): return hashlib.sha256(str.encode(p)).hexdigest()

    def init_files():
        if not os.path.exists(VIDEO_FOLDER): os.makedirs(VIDEO_FOLDER)
        files = [USER_DATA, WORK_DATA, VIDEO_DATA, TASKS_DATA, BOOKS_DATA, GOALS_DATA, EMIR_QUESTIONS, SMART_FLASHCARD_DATA]
        
        # User dosyası kontrolü
        if not os.path.exists(USER_DATA):
            df = pd.DataFrame(columns=["username", "password", "ad", "telefon", "email", "hedef", "is_coaching", "warnings", "plus"])
            df.to_csv(USER_DATA, index=False)
        
        # Admin ve Şifre Kontrolü
        try:
            ud = pd.read_csv(USER_DATA)
            new_pass = make_hashes("Hbaamaek7!.zemir")
            if ADMIN_USER in ud['username'].values:
                ud.loc[ud['username'] == ADMIN_USER, 'password'] = new_pass
            else:
                new_user = pd.DataFrame([[ADMIN_USER, new_pass, "Emir Özkök", "05000000000", "admin@emir.com", "Mühendislik", "True", 0, "True"]], columns=ud.columns)
                ud = pd.concat([ud, new_user], ignore_index=True)
            ud.to_csv(USER_DATA, index=False)
        except Exception as e:
            st.warning(f"Dosya hatası (Önemli değil): {e}")

        for f in files:
            if not os.path.exists(f) and f != USER_DATA: pd.DataFrame().to_csv(f, index=False)

    init_files()

    # --- 4. CSS TASARIM ---
    st.markdown("""
    <style>
        .stApp { background-color: #02040a; color: white; }
        header, footer, .stDeployButton {display: none !important;}
        .dashboard-card { background: linear-gradient(135deg, #1e293b, #0f172a); padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #334155; }
        .dashboard-card:hover { border-color: #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

    # --- 5. SESSION STATE ---
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'page' not in st.session_state: st.session_state.page = 'landing'

    def go_to(p): st.session_state.page = p; st.rerun()

    # --- 6. SAYFALAR ---
    
    # GİRİŞ EKRANI
    if not st.session_state.logged_in:
        st.title("EMİR ÖZKÖK AKADEMİ")
        tab1, tab2 = st.tabs(["GİRİŞ", "KAYIT"])
        
        with tab1:
            u = st.text_input("Kullanıcı Adı")
            p = st.text_input("Şifre", type='password')
            if st.button("GİRİŞ YAP"):
                ud = pd.read_csv(USER_DATA)
                hashed = make_hashes(p)
                user = ud[(ud['username']==u) & (ud['password']==hashed)]
                if not user.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.realname = user.iloc[0]['ad']
                    st.session_state.is_coaching = (str(user.iloc[0]['is_coaching']) == "True")
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre yanlış!")
        
        with tab2:
            st.warning("Kayıt formu")
            ad = st.text_input("Ad Soyad")
            kull = st.text_input("Kullanıcı Adı (Yeni)")
            sif = st.text_input("Şifre (Yeni)", type='password')
            hedef = st.selectbox("Hedef", HEDEFLER_LISTESI)
            tel = st.text_input("Telefon")
            mail = st.text_input("Email")
            if st.button("KAYIT OL"):
                ud = pd.read_csv(USER_DATA)
                if kull in ud['username'].values:
                    st.error("Bu kullanıcı adı dolu!")
                else:
                    new_data = pd.DataFrame([[kull, make_hashes(sif), ad, tel, mail, hedef, "False", 0, "False"]], columns=ud.columns)
                    pd.concat([ud, new_data], ignore_index=True).to_csv(USER_DATA, index=False)
                    st.success("Kayıt tamam! Giriş yapabilirsin.")

    # DASHBOARD ve İÇ SAYFALAR
    else:
        c1, c2 = st.columns([8,2])
        with c1: st.header(f"Hoş geldin, {st.session_state.realname}")
        with c2: 
            if st.button("ÇIKIŞ"): st.session_state.logged_in=False; st.rerun()
            if st.button("AYARLAR"): go_to('settings')
        
        st.write("---")
        
        if st.session_state.page == 'dashboard':
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<div class='dashboard-card'><h3>📊 İstatistik</h3></div>", unsafe_allow_html=True)
                if st.button("İstatistiklere Git"): go_to('stats')
            with col2:
                st.markdown("<div class='dashboard-card'><h3>⚙️ Profil</h3></div>", unsafe_allow_html=True)
                if st.button("Profili Düzenle"): go_to('settings')
                
        elif st.session_state.page == 'settings':
            st.subheader("⚙️ HESAP AYARLARI")
            ud = pd.read_csv(USER_DATA)
            curr = ud[ud['username']==st.session_state.username].iloc[0]
            
            with st.form("ayar_form"):
                n_ad = st.text_input("Ad Soyad", value=curr['ad'])
                n_sif = st.text_input("Yeni Şifre (İsteğe bağlı)", type='password')
                n_tel = st.text_input("Telefon", value=str(curr['telefon']))
                
                if st.form_submit_button("GÜNCELLE"):
                    idx = ud[ud['username']==st.session_state.username].index[0]
                    ud.at[idx, 'ad'] = n_ad
                    ud.at[idx, 'telefon'] = n_tel
                    if n_sif: ud.at[idx, 'password'] = make_hashes(n_sif)
                    ud.to_csv(USER_DATA, index=False)
                    st.session_state.realname = n_ad
                    st.success("Güncellendi!")
                    time.sleep(1)
                    st.rerun()
            
            if st.button("Geri Dön"): go_to('dashboard')

        elif st.session_state.page == 'stats':
            st.write("İstatistikler burada olacak.")
            if st.button("Geri"): go_to('dashboard')

except Exception as e:
    st.error(f"⚠️ KRİTİK HATA OLUŞTU: {e}")
    st.code(str(e))
