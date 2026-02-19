import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, date, timedelta
import time
import base64
import glob
import random
import re

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
FLASHCARD_IMG_FOLDER = "flashcard_images"

# --- YÖNETİCİ BİLGİLERİ ---
ADMIN_USER = "emirozkok"
ADMIN_PASS_RAW = "Hbaamaek7!.zemir" 

# --- 📋 MÜFREDAT (EXCEL BİREBİR AKTARILDI - TYT VE AYT SAYISAL) ---
CIZELGE_DETAY = {
    "TYT TÜRKÇE": [
        "Ses Bilgisi", "Yazım Kuralları", "Noktalama İşaretleri", "Sözcükte Anlam",
        "Cümlede Anlam", "Paragraf Anlam", "İsim Sıfat Zamir", "Tamlamalar", "Zarf",
        "Edat-Bağlaç-Ünlem", "Fiil Çekimi", "Fiilde Çatı", "Fiilimsi", "Ek Fiil",
        "Sözcük Yapısı", "Cümlenin Ögeleri Türleri", "Anlatım Bozuklukları"
    ],
    "TYT MATEMATİK": [
        "Sayı Kümeleri", "Sayı Basamakları", "Asal Sayılar-Faktöriyel", "Bölme-Bölünebilme",
        "Ebob-Ekok (Ortak Bölen ve Katlar)", "Tekrar Eden Durum Problemler", "Rasyonel Sayılar",
        "Birinci Dereceden Bir Bilinmeyenli Denklemler", "Denklem Sistemleri", "Basit Eşitsizlikler",
        "Mutlak Değer", "Üslü Sayılar", "Köklü Sayılar", "Oran-Orantı-Problemleri",
        "Sayı - Kesir Problemleri", "Yaş Problemleri", "Yüzde-Kar-Zarar Problemleri",
        "Karışım Problemleri", "İşçi Problemleri", "Hareket Problemleri", "Grafik Problemleri",
        "Sayısal Yetenek Problemleri", "Kümeler", "Mantık", "Polinom", "Permütasyon",
        "Kombinasyon", "Olasılık", "Çarpanlara Ayırma", "Fonksiyonlar"
    ],
    "AYT MATEMATİK": [
        "Fonksiyonlar Giriş", "Fonksiyon Türleri", "Ters Fonksiyon", "Fonksiyon Grafikleri",
        "Fonksiyonlarda Simetri Öteleme", "Logaritma", "Diziler (Aritmetik-Geometrik)",
        "Trigonometri-1", "Trigonometri-2", "Çarpanlara Ayırma", "Polinom",
        "İkinci Dereceden Denklemler", "Parabol", "Eşitsizlikler", "Limit",
        "Sağ Sol Limit - Limit Özellikleri", "Parçalı Fonksiyon Limitleri", "Limitte Belirsizlik",
        "Süreklilik", "Türev", "Ortalama Değişim Oranı", "Türevin Geometrik Tanımı - Türev Alma Kuralları",
        "Sağdan Soldan Türev", "Türev Süreklilik İlişkisi", "Türevin Fiziksel Yorumu",
        "Rolle Teoremi ve Ortalama Değer Teoremi", "Art. Azalan Fonk(Türevle İlişkisi)",
        "Ekstremum Noktalama Max Min", "Polinom Fonksiyonlarının Grafiğ. Çizilmesi",
        "Türevin Geometrik Yorumu", "Maksimum ve Minimum Problemleri", "İntegral",
        "Diferansiyel", "İntegralin Özellikleri ve İntegral Alma Kuralları",
        "Değişken Değiştirme Yöntemi", "Belirli İntegral ve Özellikleri",
        "Parçalı Fonksiyonların İntegrali", "Rieman Toplamı", "İntegralde Alan Bulma"
    ],
    "GEOMETRİ": [
        "Doğruda Açılar", "Üçgende Açılar", "Dik Üçgen", "İkizkenar Üçgen", "Eşkenar Üçgen",
        "Üçgende Alan", "Açıortay", "Kenarortay", "Üçgende Benzerlik", "Açı-Kenar Bağıntıları",
        "Çokgenler", "Dörtgenler", "Deltoid", "Paralelkenar", "Eşkenar Dörtgen", "Dikdörtgen",
        "Kare", "Yamuk", "Çemberde Açı", "Çemberde Uzunluk", "Dairede Alan", "Katı Cisimler",
        "Nokt. Analitik İncelenmesi", "Doğr. Analitik İncelenmesi", "Dönüşümlerle Geometri",
        "Çembr. Analitik İncelenmesi"
    ],
    "TYT FİZİK": [
        "Fiziğin Doğası", "Madde ve Özellikleri", "Kaldırma Kuvveti", "Basınç", "Isı Sıcaklık",
        "Genleşme", "Doğrusal Hareket", "Newtn Hrkt Yasaları (Dinamik)", "Atışlar", "Aydınlanma",
        "Gölge", "Düzlem Ayna", "Küresel Aynalar", "Renkler", "Kırılma", "Mercekler",
        "Temel Dalga Bilgileri ve Ses Dalgası", "Yay Dalgaları", "Su Dalgaları",
        "Elektrostatik-Coulomb Kuvveti", "Elektrik Akımı Devreler", "Manyetizma (Mıknatıs, M. Alan)"
    ],
    "AYT FİZİK": [
        "Vektör-Kuvvet", "Denge-Tork", "Kütle Merkezi", "Basit Makinalar", "Doğrusal Hareket",
        "Bağıl Hareket - Nehir Prb", "Newtn Hrkt Yasaları (Dinamik)", "Atışlar", "İş-Güç-Enerji",
        "İtme Momentum", "Düzgün Çembersel Hareket", "Basit Harmonik Hareket", "Açısal Momentum",
        "Genel Çekim-Kepler Yasaları", "Su Dalgaları Girişim", "Işık Teorileri",
        "Elektrostatik-Coulomb Kuvveti", "Elektriksel Alan", "Elektriksel Potansiyel İş Levhalar",
        "Kondansatörler", "Manyetik Kuvvet, İnd. Özind.", "Alternatif Akım Devreleri",
        "Transformatör", "Fotoelektrik-Compton-De Broglie", "Atom Teorileri",
        "Çekirdek Fiziği + Radyoaktivite", "Atomlardan Kuarklara", "E.M.D. - X-Işınları",
        "Özel Görelilik", "Katı Hal Fiziği-Elektr. Devre Elemanları", "Modern Fiziğin Teknolojideki Uygulamaları"
    ],
    "TYT KİMYA": [
        "Kimya Bilimi (Simya)", "Atom Yapısı", "Periyodik Cetvel", "Kimyanın Temel Kanunları",
        "Kimyasal Tür.Arası Etk.(İyonik Kovalent - Zayıf Bağ)", "Mol Kavramı", "Kimyasal Tepk. Denklemleri",
        "Kimyasal Hesaplamalar", "Maddenin Halleri", "Karışımlar - Karışımların Ayrılması",
        "Asit - Baz - Tuz", "Kimya Her Yerde"
    ],
    "AYT KİMYA": [
        "Modern Atom Teorisi", "Periyodik Sistem ve Özk.", "Kimya ve Elektrik Redoks",
        "Elektrokimyasal Piller + Elektroliz", "Gaz Yasaları İdeal Gaz Denk.", "Gaz Karışımları, Kısmi Basınç",
        "Gerçek Gaz Su Üst. Toplanma", "Çözeltiler", "Karışımlar - Karışımların Ayrılması",
        "Kimyasal Tep. Enerji", "Kimyasal Tep. Hız", "Kimyasal Tep. Denge", "Dengeyi Etkileyen Faktörler",
        "Sulu Çözeltilerde Asit Baz Deng", "Çözünme - Çökelme Dengeleri", "Karbon Kimyasına Giriş",
        "Organik Bileşikler Hidrokarbonlar", "Aromatik Bileşikler", "Fonksiyonel Gruplar 1-2", "Hayatımızda Kimya"
    ],
    "TYT BİYOLOJİ": [
        "Canlıların Ortak Özellikleri", "Can. Temel Bil.-İnorganik Bileşikler", "Organik Bileşikler",
        "Enzim ve Nükleik Asitler", "Hücre", "Hücre Zarından Madde Geçişleri", "Organeller",
        "Canlıların Sınıflandırılması", "Virüsler, Bakteriler ve Arkeler", "Protista ve Mantarlar",
        "Bitkiler Hayvanlar", "Mitoz Bölünme", "Eşeysiz Üreme", "Mayoz Bölünme", "Eşeyli Üreme",
        "Kalıtımın Esas İlkeleri", "Çaprazlamalar", "Eksik ve Eş Baskınlık - Pleiotropi - Çok Alellilik-Kan Grupları",
        "Eşeye Bağlı Kalıtım - Kalıtsal Çeşitlilik", "Ekolojik Kavramlar", "Canlıların Beslenme İlişkileri",
        "Besin Zinciri Enerji Akışı", "Madde Döngüleri", "Güncel Çevre Sorunları"
    ],
    "AYT BİYOLOJİ": [
        "Sinir Sistemi", "Merkezi Sinir Sistemi", "Endokrin Sistem(Hormon Özellikleri-Hipofiz Bezi Hormonları)",
        "Tiroid Bezi - Böbrek Üstü Bezler, Eşeysel Hormonlar", "Duyu Organları (Göz-Kulak)", "Burun - Dil - Deri",
        "Destek ve Hareket Sistemi (İskelet)", "Kaslar - Kasların Çalışması", "Sindirim Sistemi (Organlar)",
        "Besinlerin Sindirimi", "Dolaşım Sistemi (Kalp)", "Kan Damarları, Kan - Doku", "Bağışıklık Sistemi",
        "Solunum Sistemi (Organlar)", "Soluk Alıp Verme - Solunum Gazlarının Taşınması", "Üriner Sistem(Organlar)",
        "İdrarın Oluşumu", "Üreme Sistemi", "Döllenme,Büyüme ve Gelişme", "Komünite -Popülasyon Ekolojisi",
        "Nükleik Asitler - Prot", "Protein Sentezi-Biyoteknoloji", "Fotosentez", "Solunum",
        "Bitki Biyolojisi(Bitkisel Organlar)", "Bitkilerde Hareket, Hormonlar, Beslenme"
    ]
}

# --- 📚 KİTAP ÖNERİ SİSTEMİ (LİSTEDEN ÇEKİLDİ) ---
KITAP_ONERILERI = {
    "TYT TÜRKÇE": [
        "Hız ve Renk (Kolay)", "Aydınetap Paragraf (Kolay)", 
        "345 (Orta)", "Bilgi Sarmal (Orta)", "Paragrafın Ritmi (Orta)", "Apotemi Paragraf (Orta)", "Yayın Denizi Dilbilgisi (Orta)",
        "Limit (Orta-Zor)", "IQ (Zor)", "Paraf (Zor)", "Sıfır Risk (Zor)", "3D (Zor)", "Paragrafın Şifresi (Zor)"
    ],
    "TYT MATEMATİK": [
        "345 Start (Kolay)", "Metin Parkur (Kolay)", "Aktif (Kolay)", "Karekök 0 (Kolay)", "Mikro (Kolay)",
        "Full (Orta)", "345 (Orta)", "Bilgi Sarmal (Orta)", "Miray (Orta)", "Toprak (Orta)",
        "Metin (Orta-Zor)", "Acil (Orta-Zor)",
        "Orijinal (Zor)", "3D (Zor)", "Barış (Zor)"
    ],
    "AYT MATEMATİK": [
        "Hız ve Renk (Kolay)", "Karekök 0 (Kolay)",
        "Palme (Orta)", "345 (Orta)", "Bilgi Sarmal (Orta)",
        "3D VDD Eyüp B (Zor)", "Orijinal (Zor)"
    ],
    "GEOMETRİ": [
        "Mikro Geometrinin İlacı (Kolay-Orta)",
        "Acil (Orta)", "Hız ve Renk (Orta)", "345 (Orta)",
        "Orijinal (Zor)", "Rasyonel (Zor)", "Bilgi Sarmal (Zor)", "Metin (Zor)", "Çap Fasikülleri (Zor)", "EİS (Zor)", "Apotemi (Zor)"
    ],
    "TYT FİZİK": [
        "4K (Kolay-Orta)", "345 (Kolay-Orta)", "Negro (Kolay-Orta)",
        "3D (Orta-Zor)", "Bilgi Sarmal (Orta-Zor)", "Apotemi (Orta-Zor)", "Esen (Orta-Zor)"
    ],
    "AYT FİZİK": [
        "Paylaşım Konu Anlatım Fasikülleri (Kolay-Orta)",
        "3D (Orta)", "Paraf (Orta)", "IQ (Orta)", "Bilgi Sarmal (Orta)", "Ulti (Orta)", "345 (Orta)"
    ],
    "TYT KİMYA": [
        "Miray Konu Anlatımı", "Aktif Kimya (Kolay)", "Eğitim Vadisi (Kolay)",
        "Orbital (Orta)", "Bilgi Sarmal (Orta)", "345 (Orta)", "Aydın (Orta)", "4K (Orta)"
    ],
    "AYT KİMYA": [
        "Görkem Şahin TYT / Aktif (Başlangıç)",
        "Palme (Orta)", "Orbital (Orta)", "Bilgi Sarmal (Orta)", "Miray (Orta)", "Apotemi (Orta)",
        "Aydın (Zor)", "VAF (Zor)"
    ],
    "TYT BİYOLOJİ": [
        "Palme (Normal)", "Karekök (Normal)", "Çap (Normal)", "Okyanus (Normal)", "Bilgi Sarmal (Normal)",
        "Acil (Zor)", "Aydın (Zor)", "3D (Zor)"
    ],
    "AYT BİYOLOJİ": [
        "Palme AYT Sıfır (Kolay)", "Çap Kolay (Kolay)", "Okyanus Pratik (Kolay)",
        "Palme (Orta)", "3D (Orta)", "Bilgi Sarmal (Orta)",
        "Acil (Zor)", "Aydın (Zor)", "Limit (Zor)", "Endemik (Zor)"
    ]
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
        df = pd.read_csv(file_path)
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False)
        return df

def make_hashes(p): return hashlib.sha256(str.encode(p)).hexdigest()

def init_files():
    if not os.path.exists(VIDEO_FOLDER): os.makedirs(VIDEO_FOLDER)
    if not os.path.exists(FLASHCARD_IMG_FOLDER): os.makedirs(FLASHCARD_IMG_FOLDER)
    
    safe_read_csv(WORK_DATA, ["username", "Tarih", "Ders", "Konu", "Soru", "Süre"])
    safe_read_csv(TASKS_DATA, ["id", "username", "book", "ders", "konu", "gorev", "durum", "tarih"])
    safe_read_csv(BOOKS_DATA, ["username", "book_name", "category", "status"])
    safe_read_csv(GOALS_DATA, ["username", "date", "target_min", "status"])
    safe_read_csv(EMIR_QUESTIONS, ["id", "Tarih", "Kullanici", "Soru", "Durum"])
    safe_read_csv(SMART_FLASHCARD_DATA, ["username", "ders", "soru", "cevap", "tarih", "image_path"])
    safe_read_csv(TRIALS_DATA, ["username", "tarih", "tur", "yayin", "net", "detay"])
    safe_read_csv(VIDEO_DATA, ["baslik", "dosya_yolu"])

    if not os.path.exists(USER_DATA) or os.stat(USER_DATA).st_size == 0:
        df = pd.DataFrame(columns=["username", "password", "ad", "telefon", "email", "hedef", "is_coaching", "warnings", "plus"])
        admin_data = pd.DataFrame([[ADMIN_USER, make_hashes(ADMIN_PASS_RAW), "Emir Özkök", "05000000000", "admin@emir.com", "Mühendislik", "True", 0, "True"]], columns=df.columns)
        df = pd.concat([df, admin_data], ignore_index=True)
        df.to_csv(USER_DATA, index=False)
    else:
        try:
            ud = safe_read_csv(USER_DATA, ["username", "password", "ad", "telefon", "email", "hedef", "is_coaching", "warnings", "plus"])
            if ADMIN_USER in ud['username'].values:
                ud.loc[ud['username'] == ADMIN_USER, 'password'] = make_hashes(ADMIN_PASS_RAW)
                ud['is_coaching'] = ud['is_coaching'].astype(str)
                ud.to_csv(USER_DATA, index=False)
        except Exception: pass

init_files()

# --- 🚀 GLOBAL KRONOMETRE GÖSTERGESİ ---
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


# --- 🎨 CSS: GENEL & NEON PARLAMALAR ---
st.markdown("""
<style>
    .stApp { background-color: #02040a; color: #e2e8f0; font-family: 'Inter', sans-serif; }
    header, footer, #MainMenu, .stDeployButton, div[class^='viewerBadge'] {display: none !important;}
    
    /* EN ALTTA DEV BOŞLUK - HİÇBİR ŞEY DİBE YAPIŞAMAZ */
    .block-container { padding-top: 1rem !important; padding-bottom: 250px !important; }

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
    
    /* NEON INPUT & BUTON EFEKTLERİ */
    div.stTextInput > div > div > input, div.stSelectbox > div > button, div.stNumberInput > div > div > input { 
        background-color: #0f172a !important; 
        color: white !important; 
        border: 2px solid #1e293b !important; 
        transition: all 0.3s ease-in-out !important;
        border-radius: 8px !important;
    }
    div.stTextInput > div > div > input:focus, div.stSelectbox > div > button:focus, div.stNumberInput > div > div > input:focus {
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.7) !important;
        border-color: #3b82f6 !important;
    }

    div.stButton > button { 
        background-color: transparent; color: white; border: 1px solid rgba(255,255,255,0.2); 
        font-weight: bold; width: 100%; transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #3b82f6; border-color: #3b82f6;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.7);
    }

    .teams-link {
        display: block; width: 100%; padding: 15px;
        background: linear-gradient(90deg, #10b981, #059669); 
        color: white !important; text-align: center; border-radius: 12px;
        text-decoration: none; font-weight: bold; font-size: 18px;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4); transition: 0.3s;
    }
    .teams-link:hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.8); }
    
    /* GİRİŞ EKRANI NEON TAB PARLAMASI */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        flex-grow: 1 !important;
        text-align: center !important;
        justify-content: center !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        transition: 0.3s;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #60a5fa !important;
        text-shadow: 0 0 10px rgba(96, 165, 250, 0.8);
    }
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
    
    st.markdown("""
    <style>
    div[data-testid="stTabs"] {
        background: rgba(15, 23, 42, 0.9);
        padding: 30px 30px 45px 30px; 
        border-radius: 20px;
        border: 2px solid #3b82f6; 
        box-shadow: 0 0 40px rgba(59, 130, 246, 0.5), inset 0 0 20px rgba(59, 130, 246, 0.1); 
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #3b82f6 !important;
        box-shadow: 0 0 10px #3b82f6;
    }
    div[data-baseweb="tab-border"] {
        background-color: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align:center; font-size: 70px; color:#3b82f6; margin-bottom:10px; text-shadow: 0 0 25px rgba(59,130,246,0.7);'>EMİR ÖZKÖK</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align:center; margin-bottom: 40px; padding: 0 10%;'>
        <p style='color:#cbd5e1; font-size:20px; line-height:1.6;'>
        Sınav senesinde <b>"keşke böyle bir site olsaydı"</b> diyeceğim şekilde, ihtiyaçlarına göre bir site hazırladım. 
        İçeride yaptıklarını kaydedebileceğin, ne kadar soru çözdüğünü anlık görebileceğin, önemli bilgileri not edip flash kartlarla çalışabileceğin bölümler ve daha nicesi...
        </p>
        <p style='color:#3b82f6; font-weight:bold; font-size:24px; margin-top:15px; text-shadow: 0 0 10px rgba(59,130,246,0.4);'>
        HADİ HEMEN BAŞLA! 🚀
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.1], gap="large")
    
    with col1:
        found_files = glob.glob("emir_foto.*") + glob.glob("emir*.*")
        photo_path = None
        for f in found_files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.jpg.jpg')): photo_path = f; break
        
        if photo_path:
            with open(photo_path, "rb") as image_file: encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'''
            <div style="width:100%; max-width: 420px; margin: 0 auto; aspect-ratio: 4/5; border-radius:20px; border:2px solid #3b82f6; box-shadow: 0 0 30px rgba(59, 130, 246, 0.4); overflow:hidden;">
                <img src="data:image/png;base64,{encoded_string}" style="width:100%; height:100%; object-fit:cover; object-position: top;">
            </div>
            ''', unsafe_allow_html=True)

    with col2:
        tab1, tab2 = st.tabs(["🔐 GİRİŞ YAP", "📝 ÜYE OL"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            u = st.text_input("Kullanıcı Adı", key="l_u")
            p = st.text_input("Şifre", type='password', key="l_p")
            st.markdown("<br>", unsafe_allow_html=True)
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
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("KAYDI TAMAMLA", use_container_width=True):
                if not n or not ru or not rp: st.error("Boş alan bırakma.")
                else:
                    try:
                        ud = safe_read_csv(USER_DATA, ["username", "password", "ad", "telefon", "email", "hedef", "is_coaching"])
                        if ru not in ud['username'].values:
                            new_user = pd.DataFrame([[ru, make_hashes(rp), n, rt, rm, rh, "False"]], columns=["username", "password", "ad", "telefon", "email", "hedef", "is_coaching"])
                            pd.concat([ud, new_user], ignore_index=True).to_csv(USER_DATA, index=False)
                            st.success("Kayıt Başarılı! 'Giriş Yap' sekmesine tıkla.")
                        else: st.error("Kullanıcı adı alınmış.")
                    except Exception as e: st.error(f"Kayıt hatası: {e}")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 40px; padding: 25px; background: rgba(16, 185, 129, 0.1); border-radius: 15px; border: 1px dashed rgba(16, 185, 129, 0.4);">
            <p style="color: #cbd5e1; font-size: 15px; margin-bottom: 15px; font-weight: 500;">Hazır çalışma programları, grup rehberlik etkinlikleri, derece yaptıran taktikler ve <b>Emir Özkök'e doğrudan soru sorma şansı</b> için topluluğa da katıl 👇</p>
            <a href="https://teams.live.com/l/community/FEA37u2Ksl3MjtjcgY" target="_blank" class="teams-link">
                🔥 KAZANANLARIN BAHANESİ OLMAZ (+50 ÜYE)
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

# ==========================================
# 2. DASHBOARD
# ==========================================
elif st.session_state.logged_in and st.session_state.page == 'dashboard':
    
    render_floating_timer()
    
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
            st.markdown('''
            <a href="https://teams.live.com/l/community/FEA37u2Ksl3MjtjcgY" target="_blank" style="text-decoration:none;">
                <div class="dashboard-card card-dark">
                    <h3>💬 TOPLULUĞA GİT</h3>
                    <p>Emir Özkök'e Soru Sor</p>
                </div>
            </a>
            ''', unsafe_allow_html=True)
        with r2_c2:
            st.markdown('<div class="dashboard-card card-purple" style="background: linear-gradient(135deg, #E91E63, #9C27B0);"><h3>🧠 KARTLAR</h3><p>Soru & Çözüm Defteri</p></div>', unsafe_allow_html=True)
            if st.button("ÇALIŞ", use_container_width=True): go_to('flashcards')

        if st.session_state.username == ADMIN_USER:
            st.markdown("---")
            a1, a2, a3 = st.columns(3)
            with a1: 
                if st.button("KİTAPLARI YÖNET"): go_to('admin_books')
            with a2: 
                if st.button("ÖĞRENCİ LİSTESİ"): go_to('admin_users')
            with a3:
                if st.button("💾 YEDEKLE / GERİ YÜKLE"): go_to('admin_backup')
                
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

# ==========================================
# 3. İÇ SAYFALAR
# ==========================================
elif st.session_state.logged_in:
    render_floating_timer()
    
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
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("GÜNCELLE"):
                    idx = ud[ud['username']==st.session_state.username].index[0]
                    ud.at[idx, 'ad'] = na
                    ud.at[idx, 'telefon'] = nt
                    ud.at[idx, 'hedef'] = nh
                    if np and len(np)>6: ud.at[idx, 'password'] = make_hashes(np)
                    ud.to_csv(USER_DATA, index=False)
                    st.session_state.realname = na
                    st.success("Bilgiler güncellendi!"); time.sleep(1); st.rerun()
        except Exception as e: st.error(f"Ayar hatası: {e}")
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

    elif st.session_state.page == 'admin_users':
        st.header("👥 Öğrenci Yönetimi")
        st.info("❗ Koçluk yetkisi vermek için 'is_coaching' kutucuğunu işaretle ve KAYDET butonuna bas.")
        ud = safe_read_csv(USER_DATA, ["username", "is_coaching"])
        ud['is_coaching'] = ud['is_coaching'].apply(lambda x: str(x).lower() in ['true', '1', 'yes'])
        edited_df = st.data_editor(ud, num_rows="dynamic", column_config={"is_coaching": st.column_config.CheckboxColumn("Koçluk Öğrencisi mi?", default=False)})
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 DEĞİŞİKLİKLERİ KAYDET"):
            edited_df['is_coaching'] = edited_df['is_coaching'].astype(str)
            edited_df.to_csv(USER_DATA, index=False)
            st.success("Veriler güncellendi!")
            time.sleep(1); st.rerun()
            
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

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
            
            st.markdown("<br>", unsafe_allow_html=True)
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
            st.markdown("<br>", unsafe_allow_html=True)
            if c_b.button("Süreyi Kaydet"):
                toplam_dk = (saat * 60) + dakika
                if toplam_dk > 0:
                    df = safe_read_csv(WORK_DATA, ["username","Tarih","Ders","Konu","Soru","Süre"])
                    new_row = pd.DataFrame([[st.session_state.username, str(selected_date), "GENEL", "Günlük Süre", 0, toplam_dk]], columns=df.columns)
                    pd.concat([df, new_row], ignore_index=True).to_csv(WORK_DATA, index=False)
                    st.success(f"Toplam {saat} saat {dakika} dakika kaydedildi!")
                else: st.warning("Süre girmedin.")
            
            st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

        with tab_deneme:
            st.subheader("🏆 Deneme Sınavı Ekle")
            
            t_tur = st.selectbox("Deneme Türü Seç:", ["TYT", "AYT Sayısal", "AYT Eşit Ağırlık", "AYT Sözel", "Branş Denemesi"])
            
            with st.form("trial_form"):
                c_t1, c_t2 = st.columns(2)
                t_date = c_t1.date_input("Deneme Tarihi", date.today())
                t_yayin = c_t2.text_input("Yayın Evi (Örn: 345, Bilgi Sarmal)")
                
                st.markdown("---")
                st.markdown("#### 📝 Doğru ve Yanlışlarını Gir (Netler Otomatik Hesaplanır)")
                
                if t_tur == "TYT":
                    c_n1, c_n2, c_n3, c_n4 = st.columns(4)
                    with c_n1:
                        st.markdown("**Türkçe (40)**")
                        t_d = st.number_input("D", 0, 40, key="t_d")
                        t_y = st.number_input("Y", 0, 40, key="t_y")
                        turkce = t_d - (t_y * 0.25)
                    with c_n2:
                        st.markdown("**Sosyal (20)**")
                        s_d = st.number_input("D", 0, 20, key="s_d")
                        s_y = st.number_input("Y", 0, 20, key="s_y")
                        sosyal = s_d - (s_y * 0.25)
                    with c_n3:
                        st.markdown("**Matematik (40)**")
                        m_d = st.number_input("D", 0, 40, key="m_d")
                        m_y = st.number_input("Y", 0, 40, key="m_y")
                        mat = m_d - (m_y * 0.25)
                    with c_n4:
                        st.markdown("**Fen (20)**")
                        f_d = st.number_input("D", 0, 20, key="f_d")
                        f_y = st.number_input("Y", 0, 20, key="f_y")
                        fen = f_d - (f_y * 0.25)

                elif t_tur == "AYT Sayısal":
                    c_n1, c_n2, c_n3, c_n4 = st.columns(4)
                    with c_n1:
                        st.markdown("**Matematik (40)**")
                        m_d = st.number_input("D", 0, 40, key="m_d")
                        m_y = st.number_input("Y", 0, 40, key="m_y")
                        mat = m_d - (m_y * 0.25)
                    with c_n2:
                        st.markdown("**Fizik (14)**")
                        f_d = st.number_input("D", 0, 14, key="f_d")
                        f_y = st.number_input("Y", 0, 14, key="f_y")
                        fizik = f_d - (f_y * 0.25)
                    with c_n3:
                        st.markdown("**Kimya (13)**")
                        k_d = st.number_input("D", 0, 13, key="k_d")
                        k_y = st.number_input("Y", 0, 13, key="k_y")
                        kimya = k_d - (k_y * 0.25)
                    with c_n4:
                        st.markdown("**Biyoloji (13)**")
                        b_d = st.number_input("D", 0, 13, key="b_d")
                        b_y = st.number_input("Y", 0, 13, key="b_y")
                        biyo = b_d - (b_y * 0.25)
                
                elif t_tur == "AYT Eşit Ağırlık":
                    c_n1, c_n2, c_n3, c_n4 = st.columns(4)
                    with c_n1:
                        st.markdown("**Matematik (40)**")
                        m_d = st.number_input("D", 0, 40, key="ea_m_d")
                        m_y = st.number_input("Y", 0, 40, key="ea_m_y")
                        mat = m_d - (m_y * 0.25)
                    with c_n2:
                        st.markdown("**Edebiyat (24)**")
                        e_d = st.number_input("D", 0, 24, key="e_d")
                        e_y = st.number_input("Y", 0, 24, key="e_y")
                        edebiyat = e_d - (e_y * 0.25)
                    with c_n3:
                        st.markdown("**Tarih-1 (10)**")
                        t1_d = st.number_input("D", 0, 10, key="t1_d")
                        t1_y = st.number_input("Y", 0, 10, key="t1_y")
                        tarih1 = t1_d - (t1_y * 0.25)
                    with c_n4:
                        st.markdown("**Coğrafya-1 (6)**")
                        c1_d = st.number_input("D", 0, 6, key="c1_d")
                        c1_y = st.number_input("Y", 0, 6, key="c1_y")
                        cog1 = c1_d - (c1_y * 0.25)

                elif t_tur == "AYT Sözel":
                    c_n1, c_n2, c_n3, c_n4 = st.columns(4)
                    with c_n1:
                        st.markdown("**Edebiyat (24)**")
                        e_d = st.number_input("D", 0, 24, key="sz_e_d")
                        e_y = st.number_input("Y", 0, 24, key="sz_e_y")
                        edebiyat = e_d - (e_y * 0.25)
                    with c_n2:
                        st.markdown("**Tarih-1 (10)**")
                        t1_d = st.number_input("D", 0, 10, key="sz_t1_d")
                        t1_y = st.number_input("Y", 0, 10, key="sz_t1_y")
                        tarih1 = t1_d - (t1_y * 0.25)
                    with c_n3:
                        st.markdown("**Tarih-2 (11)**")
                        t2_d = st.number_input("D", 0, 11, key="t2_d")
                        t2_y = st.number_input("Y", 0, 11, key="t2_y")
                        tarih2 = t2_d - (t2_y * 0.25)
                    with c_n4:
                        st.markdown("**Coğrafya-1 (6)**")
                        c1_d = st.number_input("D", 0, 6, key="sz_c1_d")
                        c1_y = st.number_input("Y", 0, 6, key="sz_c1_y")
                        cog1 = c1_d - (c1_y * 0.25)

                else:
                    brans = st.selectbox("Branş Seç", list(CIZELGE_DETAY.keys()))
                    st.markdown("**Netin:**")
                    net_genel = st.number_input("Net", step=0.25, format="%.2f")

                st.markdown("---")
                st.markdown("<br>", unsafe_allow_html=True)
                submit_btn = st.form_submit_button("DENEMEYİ KAYDET", use_container_width=True)
                
                if submit_btn:
                    if t_tur == "TYT":
                        toplam_net = turkce + sosyal + mat + fen
                        detay_str = f"Tür: {turkce} | Sos: {sosyal} | Mat: {mat} | Fen: {fen}"
                    elif t_tur == "AYT Sayısal":
                        toplam_net = mat + fizik + kimya + biyo
                        detay_str = f"Mat: {mat} | Fiz: {fizik} | Kim: {kimya} | Biy: {biyo}"
                    elif t_tur == "AYT Eşit Ağırlık":
                        toplam_net = mat + edebiyat + tarih1 + cog1
                        detay_str = f"Mat: {mat} | Edb: {edebiyat} | Tar1: {tarih1} | Coğ1: {cog1}"
                    elif t_tur == "AYT Sözel":
                        toplam_net = edebiyat + tarih1 + cog1 + tarih2
                        detay_str = f"Edb: {edebiyat} | Tar1: {tarih1} | Coğ1: {cog1} | Tar2: {tarih2}"
                    else:
                        toplam_net = net_genel
                        detay_str = f"{brans}: {net_genel}"
                        
                    trial_df = safe_read_csv(TRIALS_DATA, ["username", "tarih", "tur", "yayin", "net", "detay"])
                    new_trial = pd.DataFrame([[st.session_state.username, str(t_date), t_tur, t_yayin, toplam_net, detay_str]], columns=trial_df.columns)
                    pd.concat([trial_df, new_trial], ignore_index=True).to_csv(TRIALS_DATA, index=False)
                    
                    st.success(f"✅ Deneme başarıyla kaydedildi! (Toplam Net: {toplam_net})")
                    time.sleep(1)
                    st.rerun()

            st.write("### 📉 Deneme Geçmişi")
            try:
                tdf = safe_read_csv(TRIALS_DATA, ["username", "tarih", "tur", "yayin", "net", "detay"])
                my_trials = tdf[tdf['username'] == st.session_state.username]
                if not my_trials.empty:
                    st.line_chart(my_trials, x="tarih", y="net")
                    st.dataframe(my_trials.sort_values(by="tarih", ascending=False)[['tarih', 'tur', 'yayin', 'net', 'detay']], use_container_width=True)
                else: st.info("Henüz deneme kaydı yok.")
            except Exception as e: st.error(f"Veri yok: {e}")
            
            st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

        with tab_grafik:
            try:
                df = safe_read_csv(WORK_DATA, ["username", "Tarih", "Ders", "Konu", "Soru", "Süre"])
                my_data = df[df['username'] == st.session_state.username]
                
                if not my_data.empty:
                    st.write("### 📊 Ders Bazlı Soru Dağılımı")
                    chart_data = my_data[my_data['Ders'] != "GENEL"].copy()
                    chart_data['Soru'] = pd.to_numeric(chart_data['Soru'], errors='coerce').fillna(0)
                    st.bar_chart(chart_data.groupby("Ders")["Soru"].sum())
                    
                    st.write("### 🗓️ Son Çalışmalar (Günlük Özet)")
                    
                    unique_dates = my_data['Tarih'].unique()
                    unique_dates.sort()
                    unique_dates = unique_dates[::-1] 
                    
                    for d in unique_dates:
                        day_data = my_data[my_data['Tarih'] == d].copy()
                        day_data['Soru'] = pd.to_numeric(day_data['Soru'], errors='coerce').fillna(0)
                        day_data['Süre'] = pd.to_numeric(day_data['Süre'], errors='coerce').fillna(0)
                        
                        toplam_soru = int(day_data['Soru'].sum())
                        toplam_sure = int(day_data['Süre'].sum())
                        
                        saat = toplam_sure // 60
                        dakika = toplam_sure % 60
                        sure_metni = f"{saat} Sa {dakika} Dk" if toplam_sure > 0 else "Süre girilmedi"
                        
                        with st.expander(f"🗓️ {d} | Toplam: {toplam_soru} Soru | ⏱️ {sure_metni}"):
                            display_df = day_data[['Ders', 'Soru', 'Süre']].copy()
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                            
                else: st.info("Henüz veri yok.")
            except Exception as e: st.error(f"Veri okuma hatası: {e}")
            
            st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

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
            st.markdown("<br>", unsafe_allow_html=True)
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
            st.markdown("<br>", unsafe_allow_html=True)
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
                        st.success("🎉 Bravo hedefine ulaştın, böyle devam! Lütfen süreni kaydet.")
                display_time = remaining
            else:
                display_time = elapsed

            mins = int(display_time // 60)
            secs = int(display_time % 60)
            st.markdown(f"<h1 style='font-size: 80px; color: #3b82f6; text-align:center;'>{mins:02d}:{secs:02d}</h1>", unsafe_allow_html=True)
            
            if st.session_state.timer_active:
                time.sleep(1); st.rerun()
                
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

    # --- 🎯 AKILLI ÖDEV ATAMA & ANALİZ SİSTEMİ (V4600) ---
    elif st.session_state.page == 'admin_cizelge':
        st.header("👑 Koçluk Komuta Merkezi")
        users = safe_read_csv(USER_DATA, ["username", "is_coaching"])
        st_list = users[(users['username'] != ADMIN_USER) & (users['is_coaching'].apply(lambda x: str(x).strip().lower() in ['true', '1', 'yes']))]['username'].tolist()
        
        if st_list:
            target = st.selectbox("🎯 Analiz Edilecek Öğrenciyi Seç", st_list)
            st.markdown("---")
            
            # --- 1. GEÇMİŞ VE İSTATİSTİKLER ---
            td = safe_read_csv(TASKS_DATA, ["id", "username", "book", "ders", "konu", "gorev", "durum", "tarih"])
            wd = safe_read_csv(WORK_DATA, ["username", "Tarih", "Ders", "Konu", "Soru", "Süre"])
            user_tasks = td[td['username'] == target].copy()
            user_work = wd[wd['username'] == target].copy()
            
            # --- 2. BİTİRİLEN KİTAPLAR MÜZESİ ---
            bd_all = safe_read_csv(BOOKS_DATA, ["username", "book_name", "category", "status"])
            
            # Dosyada status yoksa veya boşsa Active yap
            if 'status' not in bd_all.columns: bd_all['status'] = "Active"
            bd_all['status'] = bd_all['status'].fillna("Active")
            bd_all.loc[bd_all['status'] == "", 'status'] = "Active"
            
            completed_books = bd_all[(bd_all['username'] == target) & (bd_all['status'] == 'Completed')]
            if not completed_books.empty:
                with st.expander("🏆 BİTİRİLEN KİTAPLAR GURUR TABLOSU"):
                    for idx, row in completed_books.iterrows():
                        st.success(f"🏅 {row['category']} - {row['book_name']}")
                        
            st.markdown("<br>", unsafe_allow_html=True)

            # --- 3. AKILLI YENİ KİTAP EKLEME (ÖNERİ SİSTEMLİ VE GİZLİ ZORLUKLU) ---
            st.markdown("### 📚 Sisteme Yeni Kitap Ekle")
            with st.expander("➕ Yeni Kitap Tanımla (Önerileri Görmek İçin Tıklayın)"):
                bc = st.selectbox("Ders Seç", list(CIZELGE_DETAY.keys()), key="new_book_lesson")
                
                # Önerileri Çek
                oneriler = KITAP_ONERILERI.get(bc, [])
                secenekler = ["Listeden Seç..."] + oneriler + ["✍️ Kendi Kitabımı Yazacağım (Manuel)"]
                secilen_oneri = st.selectbox("Önerilen Kitaplar", secenekler)
                
                bn = ""
                if secilen_oneri == "✍️ Kendi Kitabımı Yazacağım (Manuel)":
                    bn = st.text_input("Kitap Adını Yazın:")
                elif secilen_oneri != "Listeden Seç...":
                    # ÖĞRENCİ GÖRMESİN DİYE ZORLUK SEVİYESİNİ (Parantez içini) TEMİZLİYORUZ
                    bn = re.sub(r'\s*\([^)]*\)$', '', secilen_oneri)
                    
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Kitabı Ekle"):
                    if bn:
                        new_book_df = pd.DataFrame([[target, bn, bc, "Active"]], columns=["username", "book_name", "category", "status"])
                        bd_all = pd.concat([bd_all, new_book_df], ignore_index=True)
                        bd_all.to_csv(BOOKS_DATA, index=False)
                        st.success(f"Harika! '{bn}' sisteme eklendi.")
                        time.sleep(1); st.rerun()
                    else:
                        st.error("Lütfen listeden bir kitap seçin veya adını yazın.")

            st.markdown("---")

            # --- 4. ÖDEV VERME (ÖNCE DERS SONRA KİTAP) ---
            st.markdown("### 🎯 Akıllı Ödev Atama Motoru")
            
            active_books = bd_all[(bd_all['username'] == target) & (bd_all['status'] == 'Active')]
            
            if not active_books.empty:
                available_lessons = active_books['category'].unique().tolist()
                
                c_ders, c_kitap = st.columns(2)
                filter_ders = c_ders.selectbox("1️⃣ Önce Dersi Seç", available_lessons)
                
                filtered_books = active_books[active_books['category'] == filter_ders]['book_name'].tolist()
                s_kitap = c_kitap.selectbox("2️⃣ Kitabı Seç", filtered_books)
                
                secilen_ders = filter_ders 
                
                # KİTAP RÖNTGENİ
                st.markdown(f"""
                <div style='background: #0f172a; border: 1px solid #3b82f6; border-radius: 10px; padding: 20px; margin-top: 15px; margin-bottom: 25px;'>
                    <h4 style='color: #60a5fa; margin-top: 0;'>{s_kitap} ({secilen_ders})</h4>
                """, unsafe_allow_html=True)
                
                book_tasks = user_tasks[user_tasks['book'] == s_kitap]
                tamamlananlar = book_tasks[book_tasks['durum'] == 'Tamamlandı']['konu'].unique().tolist()
                bekleyenler = book_tasks[book_tasks['durum'] == 'Yapılmadı']['konu'].unique().tolist()
                tum_konular = CIZELGE_DETAY.get(secilen_ders, ["Genel"])
                
                k_m1, k_m2, k_m3, k_m4 = st.columns(4)
                k_m1.metric("Toplam Konu", len(tum_konular))
                k_m2.metric("✅ Biten", len(tamamlananlar))
                k_m3.metric("⏳ Bekleyen", len(bekleyenler))
                k_m4.metric("Kalan", len(tum_konular) - len(tamamlananlar))
                
                if len(tum_konular) > 0:
                    prog = len(tamamlananlar) / len(tum_konular)
                    st.progress(prog, text=f"Kitap Bitirme Oranı: %{int(prog*100)}")
                    
                st.markdown("</div>", unsafe_allow_html=True)
                
                # MÜZE KONTROLÜ (Kitap bitti mi?)
                if len(tum_konular) > 0 and len(tamamlananlar) >= len(tum_konular):
                    st.balloons()
                    st.success("🎉 İNANILMAZ! Öğrenci bu kitabın müfredatındaki tüm konuları bitirmiş!")
                    if st.button("🏆 Kitabı Bitirilenler Listesine Arşivle", type="primary", use_container_width=True):
                        bd_all.loc[(bd_all['username']==target) & (bd_all['book_name']==s_kitap), 'status'] = 'Completed'
                        bd_all.to_csv(BOOKS_DATA, index=False)
                        st.rerun()
                else:
                    # NORMAL ÖDEV FORMU
                    konu_secenekleri = []
                    for k in tum_konular:
                        if k in tamamlananlar: konu_secenekleri.append(f"✅ {k} (Bitti)")
                        elif k in bekleyenler: konu_secenekleri.append(f"⏳ {k} (Ödevde)")
                        else: konu_secenekleri.append(k)
                        
                    c_form1, c_form2 = st.columns([2, 1])
                    s_konu_display = c_form1.selectbox("Hangi Konuyu Vereceksin?", konu_secenekleri)
                    s_konu_gercek = s_konu_display.replace("✅ ", "").replace(" (Bitti)", "").replace("⏳ ", "").replace(" (Ödevde)", "")
                    
                    s_detay = c_form2.text_input("Sayfa / Test Aralığı")
                    
                    if "✅" in s_konu_display: st.warning("⚠️ DİKKAT: Bu konuyu zaten BİTİRMİŞ! Emin misin?")
                    if "⏳" in s_konu_display: st.error("🚨 HATA: Bu konu şu an AKTİF ÖDEV olarak elinde bekliyor! Üst üste verme.")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🚀 ÖDEVİ GÖNDER", use_container_width=True):
                        new_task = pd.DataFrame([[int(time.time()), target, s_kitap, secilen_ders, s_konu_gercek, s_detay, "Yapılmadı", str(date.today())]], columns=["id", "username", "book", "ders", "konu", "gorev", "durum", "tarih"])
                        td = pd.concat([td, new_task], ignore_index=True)
                        td.to_csv(TASKS_DATA, index=False)
                        st.success(f"GÖREV VERİLDİ: {s_konu_gercek}")
                        time.sleep(1); st.rerun()
            else: 
                st.warning("Bu öğrenciye atanmış AKTİF bir kitap yok. Önce üstteki menüden yeni bir kitap ekleyin.")
            
            st.write("---")
            st.write(f"### 📋 {target} - Tüm Ödev Geçmişi")
            try:
                display_past = user_tasks[['tarih', 'ders', 'konu', 'gorev', 'durum', 'book']].sort_values(by="tarih", ascending=False)
                st.dataframe(display_past, use_container_width=True)
            except: st.write("Henüz ödev kaydı yok.")
            
        else: st.warning("Sistemde kayıtlı koçluk öğrencisi bulunamadı.")
        
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

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
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

    # --- 🧠 ÇÖZÜM DEFTERİ & YENİDEN ÇÖZME SİSTEMİ ---
    elif st.session_state.page == 'flashcards':
        st.header("🧠 Akıllı Kartlar & Çözüm Defteri")
        t1, t2, t3, t4 = st.tabs(["➕ Kart / Soru Ekle", "📖 Serbest Çalış", "🚀 Yeniden Çöz (Quiz)", "📋 Tümünü Gör"])
        
        with t1:
            st.subheader("Yapamadığın Soruyu veya Notunu Ekle")
            d = st.selectbox("Ders Seç", FLASHCARD_DERSLER)
            q = st.text_input("Soru (Ön Yüz)")
            a = st.text_input("Cevap (Arka Yüz)")
            
            uploaded_file = st.file_uploader("Soru Fotoğrafı Ekle (Yapamadığın soruları yükle, sonra tekrar çöz!) - PNG/JPG", type=["png", "jpg", "jpeg"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sisteme Ekle", type="primary"):
                if q and a:
                    img_path = ""
                    if uploaded_file is not None:
                        img_filename = f"flashcard_{st.session_state.username}_{int(time.time())}.png"
                        img_path = os.path.join(FLASHCARD_IMG_FOLDER, img_filename)
                        with open(img_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                            
                    fd = safe_read_csv(SMART_FLASHCARD_DATA, ["username", "ders", "soru", "cevap", "tarih", "image_path"])
                    pd.concat([fd, pd.DataFrame([[st.session_state.username, d, q, a, str(date.today()), img_path]], columns=fd.columns)]).to_csv(SMART_FLASHCARD_DATA, index=False)
                    st.success("Soru/Not başarıyla eklendi!")
                else:
                    st.error("Lütfen en azından soru ve cevap alanlarını doldur.")

        with t2:
            st.subheader("Serbest Kart Okuma")
            
            filter_opt = st.selectbox("Çalışılacak Dersi Seç", ["Tüm Dersler"] + FLASHCARD_DERSLER, key="free_filter")
            
            try:
                if 'free_card_idx' not in st.session_state: st.session_state.free_card_idx = 0
                if 'free_show_ans' not in st.session_state: st.session_state.free_show_ans = False

                fd = safe_read_csv(SMART_FLASHCARD_DATA, ["username", "ders", "soru", "cevap", "tarih", "image_path"])
                my = fd[fd['username']==st.session_state.username]
                
                if filter_opt != "Tüm Dersler":
                    my = my[my['ders'] == filter_opt]
                
                if not my.empty:
                    if st.session_state.free_card_idx >= len(my): st.session_state.free_card_idx = 0
                    row = my.iloc[st.session_state.free_card_idx]
                    
                    st.markdown(f"<div class='dashboard-card'><h5 style='color:#94a3b8;'>{row['ders']}</h5><h2>{row['soru']}</h2></div>", unsafe_allow_html=True)
                    
                    if pd.notna(row.get('image_path')) and str(row.get('image_path')) != "":
                        if os.path.exists(str(row['image_path'])):
                            st.image(str(row['image_path']), use_container_width=True)
                    
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
                else: 
                    st.warning("Bu derse ait kayıt bulunamadı.")
            except Exception as e: 
                st.error("Kayıtlar aranıyor...")

        with t3:
            st.subheader("Quizlet Modu (Soruları Yeniden Çöz ve Kendini Sına)")
            
            if 'test_queue' not in st.session_state:
                st.session_state.test_queue = []
                st.session_state.test_active = False
                st.session_state.test_show_ans = False
                st.session_state.test_user_ans = "" 

            if not st.session_state.test_active:
                test_filter = st.selectbox("Test Edilecek Dersi Seç", ["Tüm Dersler"] + FLASHCARD_DERSLER, key="test_filter")
                st.info("Seçtiğin dersin soruları RASTGELE karıştırılarak önüne gelecektir. Bilemediğin sorular destenin sonuna atılır.")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 Testi Başlat", use_container_width=True):
                    fd = safe_read_csv(SMART_FLASHCARD_DATA, ["username", "ders", "soru", "cevap", "tarih", "image_path"])
                    my = fd[fd['username']==st.session_state.username]
                    if test_filter != "Tüm Dersler":
                        my = my[my['ders'] == test_filter]
                        
                    if not my.empty:
                        my_list = my.to_dict('records')
                        random.shuffle(my_list)
                        st.session_state.test_queue = my_list
                        st.session_state.test_active = True
                        st.session_state.test_show_ans = False
                        st.session_state.test_user_ans = ""
                        st.rerun()
                    else: st.warning("Bu derse ait test edilecek kayıt yok!")
            else:
                if len(st.session_state.test_queue) == 0:
                    st.success("🎉 TEBRİKLER! Seçtiğin tüm soruları/kartları başarıyla öğrendin!")
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🔄 Yeni Test Başlat"):
                        st.session_state.test_active = False
                        st.rerun()
                else:
                    current_card = st.session_state.test_queue[0]
                    st.markdown(f"<div class='dashboard-card card-purple'><h5 style='color:#cbd5e1;'>{current_card['ders']}</h5><h2>{current_card['soru']}</h2></div>", unsafe_allow_html=True)
                    
                    if pd.notna(current_card.get('image_path')) and str(current_card.get('image_path')) != "":
                        if os.path.exists(str(current_card['image_path'])):
                            st.image(str(current_card['image_path']), use_container_width=True)
                            
                    if not st.session_state.test_show_ans:
                        user_input = st.text_input("Soruyu Çöz ve Cevabını Yaz:", key="quiz_input")
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Cevabı Kontrol Et", use_container_width=True):
                            st.session_state.test_user_ans = user_input
                            st.session_state.test_show_ans = True
                            st.rerun()
                    else:
                        gercek_cevap = str(current_card['cevap']).strip().lower()
                        ogrenci_cevap = str(st.session_state.test_user_ans).strip().lower()
                        
                        if ogrenci_cevap == gercek_cevap:
                            st.success(f"🎉 Doğru bildin, bravo! (Asıl Cevap: {current_card['cevap']})")
                        else:
                            if ogrenci_cevap == "":
                                st.info(f"💡 **Asıl Cevap:** {current_card['cevap']}")
                            else:
                                st.error(f"❌ Yanlış bildin. Doğru cevap şuydu: **{current_card['cevap']}**")
                        
                        st.write("Yine de sen karar ver, geçilsin mi tekrar mı sorulsun?")
                        c_yes, c_no = st.columns(2)
                        
                        if c_yes.button("✅ Bildim Say (Geç)", use_container_width=True):
                            st.session_state.test_queue.pop(0)
                            st.session_state.test_show_ans = False
                            st.session_state.test_user_ans = ""
                            st.rerun()
                            
                        if c_no.button("❌ Bilemedim (Tekrar Sor)", use_container_width=True):
                            card_to_move = st.session_state.test_queue.pop(0)
                            st.session_state.test_queue.append(card_to_move)
                            st.session_state.test_show_ans = False
                            st.session_state.test_user_ans = ""
                            st.rerun()
        
        with t4:
            st.subheader("📋 Sınav Öncesi Hızlı Tekrar Listesi")
            list_filter = st.selectbox("Ders Filtrele", ["Tüm Dersler"] + FLASHCARD_DERSLER, key="list_filter")
            st.markdown("<br>", unsafe_allow_html=True)
            try:
                fd = safe_read_csv(SMART_FLASHCARD_DATA, ["username", "ders", "soru", "cevap", "tarih", "image_path"])
                my = fd[fd['username']==st.session_state.username]
                
                if list_filter != "Tüm Dersler":
                    my = my[my['ders'] == list_filter]
                
                if not my.empty:
                    for i, r in my.iterrows():
                        with st.expander(f"📌 {r['ders']} | Soru: {r['soru']}"):
                            if pd.notna(r.get('image_path')) and str(r.get('image_path')) != "":
                                if os.path.exists(str(r['image_path'])):
                                    st.image(str(r['image_path']), width=300)
                            st.success(f"**Cevap:** {r['cevap']}")
                else:
                    st.info("Görüntülenecek kayıt bulunamadı.")
            except Exception:
                st.info("Kayıtlar yükleniyor...")
                
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    
    elif st.session_state.page == 'admin_books':
        st.header("Öğrenci Kitapları")
        try: st.dataframe(safe_read_csv(BOOKS_DATA, ["username", "book_name", "category", "status"]))
        except: st.write("Kitap yok")
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

    elif st.session_state.page == 'admin_backup':
        st.header("💾 YEDEKLEME VE GERİ YÜKLEME MERKEZİ")
        st.warning("⚠️ Streamlit sunucusu yeniden başladığında veriler silinebilir. Buradan düzenli olarak dosyaları indir!")
        c_down, c_up = st.columns(2)
        with c_down:
            st.subheader("⬇️ 1. Verileri İndir (Yedekle)")
            files_to_download = [USER_DATA, TASKS_DATA, WORK_DATA, BOOKS_DATA, GOALS_DATA, TRIALS_DATA, SMART_FLASHCARD_DATA]
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
        st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
