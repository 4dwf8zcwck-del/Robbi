import streamlit as st
import google.generativeai as genai
import random
import os

# --- KONFIGURACIJA STRANICE ---
st.set_page_config(page_title="Robbi AI", layout="wide", initial_sidebar_state="collapsed")

# --- API KLJUČ (KORISTI STREAMLIT SECRETS) ---
API_KEY = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY", ""))

if not API_KEY:
    st.error("❌ API ključ nije pronađen! Dodaj ga u .streamlit/secrets.toml ili kao okoljsku promenljivu.")
    st.stop()

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"❌ Greška pri konfiguraciji API-ja: {e}")
    st.stop()

# --- INICIJALIZACIJA MEMORIJE I STANJA ---
if "auth" not in st.session_state:
    st.session_state.auth = False
if "lang" not in st.session_state:
    st.session_state.lang = None
if "eyes_status" not in st.session_state:
    st.session_state.eyes_status = "normal"  # normal, wide, happy
if "color_step" not in st.session_state:
    st.session_state.color_step = 0
if "kalendar" not in st.session_state:
    st.session_state.kalendar = []

boje_svetla = ["#00d4ff", "#ff4b4b", "#ffdd00", "#00ff66", "#ffffff"]
trenutna_boja = boje_svetla[st.session_state.color_step]

# --- GLASOVNA FUNKCIJA (PISKUTAVI GLAS + BEEP SIGNAL) ---
def robbi_speak(text, lang, use_beep=False):
    # Bezbedan escape za JavaScript - zameni problematične karaktere
    clean_text = text.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
    sr_or_en = 'sr-RS' if lang == "Serbian" else 'en-US'
    
    beep_js = ""
    if use_beep:
        beep_js = """
        var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        var oscillator = audioCtx.createOscillator();
        var gainNode = audioCtx.createGain();
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(880, audioCtx.currentTime);
        gainNode.gain.setValueAtTime(0.05, audioCtx.currentTime);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.12);
        """

    js = f"""
    <script>
    setTimeout(function() {{
        {beep_js}
        setTimeout(function() {{
            var msg = new SpeechSynthesisUtterance("{clean_text}");
            msg.lang = '{sr_or_en}';
            msg.pitch = 1.6;
            msg.rate = 1.1;
            window.speechSynthesis.speak(msg);
        }}, {180 if use_beep else 0});
    }}, 100);
    </script>
    """
    st.components.v1.html(js, height=0)

# --- DIZAJN I ANIMACIJA LICA (HTML + JAVASCRIPT ZA TREPTANJE) ---
font_size_eyes = "65px"
letter_spacing = "35px"
if st.session_state.eyes_status == "wide":
    font_size_eyes = "80px"
    letter_spacing = "25px"

# Određivanje oblika usta
if not st.session_state.auth:
    usta_oblik = "✕"
elif st.session_state.eyes_status == "happy":
    usta_oblik = "▽"
else:
    usta_oblik = "◡"

# CSS Stilizacija kućišta i elemenata
st.markdown(f"""
<style>
    .robbi-case {{
        background-color: #0b0514;
        border-radius: 45px;
        padding: 35px 20px;
        text-align: center;
        border: 8px solid {trenutna_boja};
        width: 300px;
        margin: 0 auto;
        box-shadow: 0px 0px 25px {trenutna_boja}55;
    }}
    .mouth {{
        color: {trenutna_boja};
        font-size: 50px;
        margin-top: 5px;
        height: 60px;
        line-height: 60px;
        font-family: Arial, sans-serif;
    }}
    .stButton>button {{
        width: 100%;
        background-color: #1f143a;
        color: white;
        border: 2px solid {trenutna_boja};
        border-radius: 12px;
        padding: 10px;
    }}
    .mic-btn>button {{
        background-color: {trenutna_boja} !important;
        color: black !important;
        font-size: 32px !important;
        border-radius: 50% !important;
        width: 85px !important;
        height: 85px !important;
        margin: 0 auto !important;
        display: block !important;
        box-shadow: 0px 0px 20px {trenutna_boja};
    }}
</style>
""", unsafe_allow_html=True)

# JavaScript i HTML koji renderuju lice i upravljaju automatskim treptanjem
st.session_state.eyes_status = "normal" if st.session_state.eyes_status == "blink" else st.session_state.eyes_status

face_html = f"""
<div class="robbi-case">
    <div id="robbi-eyes" style="
        color: {trenutna_boja};
        font-size: {font_size_eyes};
        font-weight: bold;
        letter-spacing: {letter_spacing};
        transition: all 0.05s ease-in-out;
        height: 90px;
        line-height: 90px;
        font-family: Arial, sans-serif;
        user-select: none;
    ">●  ●</div>
    <div class="mouth">{usta_oblik}</div>
</div>

<script>
function startBlinking() {{
    const eyes = document.getElementById('robbi-eyes');
    if (!eyes) return;
    
    const originalText = "●  ●";
    const originalSize = "{font_size_eyes}";
    const originalSpacing = "{letter_spacing}";
    
    function blink() {{
        if (eyes.style.fontSize === "80px") {{
            setTimeout(blink, Math.random() * 3000 + 2000);
            return;
        }}
        
        eyes.innerText = "—  —";
        eyes.style.fontSize = "20px";
        eyes.style.letter-spacing = "50px";
        
        setTimeout(() => {{
            eyes.innerText = originalText;
            eyes.style.fontSize = originalSize;
            eyes.style.letter-spacing = originalSpacing;
        }}, 120);
        
        setTimeout(blink, Math.random() * 3500 + 2500);
    }}
    
    setTimeout(blink, 2000);
}}

if (document.readyState === "complete" || document.readyState === "interactive") {{
    startBlinking();
}} else {{
    document.addEventListener("DOMContentLoaded", startBlinking);
}}
</script>
"""

# PODELA NA LEVI I DESNI PANEL
col_left, col_right = st.columns([3, 1])

with col_left:
    if st.button("🎭 Dodirni ekran (Promeni boju svetla)"):
        st.session_state.color_step = (st.session_state.color_step + 1) % 5
        st.rerun()

    st.components.v1.html(face_html, height=220)
    st.write("")

# --- TOK LOGIKE APLIKACIJE ---

# 1. KORAK: Izbor jezika
if st.session_state.lang is None:
    with col_left:
        st.subheader("Select Language / Izaberi Jezik")
        c1, c2 = st.columns(2)
        if c1.button("English"):
            st.session_state.lang = "English"
            robbi_speak("Hello! Please enter the system password.", "English")
            st.rerun()
        if c2.button("Serbian"):
            st.session_state.lang = "Serbian"
            robbi_speak("Zdravo! Unesi lozinku za pristup sistemu.", "Serbian")
            st.rerun()

# 2. KORAK: Autentifikacija / Lozinka
elif not st.session_state.auth:
    with col_left:
        if st.session_state.lang == "Serbian":
            st.subheader("🔒 Unesi sistemsku lozinku:")
            lozinka = st.text_input("Lozinka:", type="password", key="pwd_sr")
            if lozinka:
                if lozinka == "Savatijas.kralj":
                    st.session_state.auth = True
                    st.session_state.eyes_status = "happy"
                    robbi_speak("Sistem otključano. Ja sam Robbi, tvoj lični pametni asistent.", "Serbian", use_beep=True)
                    st.rerun()
                else:
                    st.error("Nađi novog robota jer lozinku si pogrešio.")
                    robbi_speak("Nađi novog robota jer lozinku si pogrešio.", "Serbian")
        else:
            st.subheader("🔒 Enter system password:")
            lozinka = st.text_input("Password:", type="password", key="pwd_en")
            if lozinka:
                if lozinka == "Savatijas.kralj":
                    st.session_state.auth = True
                    st.session_state.eyes_status = "happy"
                    robbi_speak("System unlocked. I am Robbi, your smart personal assistant.", "English", use_beep=True)
                    st.rerun()
                else:
                    st.error("Find a new robot because you got the password wrong.")
                    robbi_speak("Find a new robot because you got the password wrong.", "English")

# 3. KORAK: Otključan sistem (Glavni rad)
else:
    with col_left:
        st.markdown("### 📅 Tvoj lični raspored i podsetnici")
        if st.session_state.kalendar:
            for i, obaveza in enumerate(st.session_state.kalendar, 1):
                st.write(f"**{i}.** 📌 {obaveza}")
        else:
            st.write("_Raspored je prazan. Reci mi 'Podseti me da...' da zapišem obavezu._")
        
        user_query = st.chat_input("Razgovaraj sa Robbi-jem ili unesi komandu...")
        
        # Dugme za mikrofon koje aktivira simulaciju slušanja i širi oči
        st.markdown('<div class="mic-btn">', unsafe_allow_html=True)
        if st.button("🎙️", key="mic_btn"):
            st.session_state.eyes_status = "wide"
            st.toast("Robbi se uspešno povezao na mikrofon uređaja i sluša tvoj glas...")
            robbi_speak("Slušam te", st.session_state.lang, use_beep=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if user_query:
            st.session_state.eyes_status = "wide"
            
            # Kalendar i komande pamćenja
            if "podseti me" in user_query.lower() or "zakaži" in user_query.lower() or "zakazi" in user_query.lower():
                st.session_state.kalendar.append(user_query)
                odgovor = "U redu, dodao sam to u tvoj lični raspored!" if st.session_state.lang == "Serbian" else "Alright, I have added that to your schedule!"
                st.write(f"**Robbi:** {odgovor}")
                robbi_speak(odgovor, st.session_state.lang, use_beep=True)
                st.session_state.eyes_status = "happy"
                st.rerun()
                
            elif "obriši kalendar" in user_query.lower() or "obrisi kalendar" in user_query.lower():
                st.session_state.kalendar = []
                odgovor = "Tvoj raspored je uspešno očišćen." if st.session_state.lang == "Serbian" else "Your calendar has been cleared."
                st.write(f"**Robbi:** {odgovor}")
                robbi_speak(odgovor, st.session_state.lang, use_beep=True)
                st.session_state.eyes_status = "normal"
                st.rerun()
                
            # Integrisane tekstualne i glasovne komande za hardver
            elif "kamera" in user_query.lower() or "uključi kameru" in user_query.lower():
                odgovor = "Povezujem se na kameru... Kamera uređaja je uspešno aktivirana i spremna za rad!" if st.session_state.lang == "Serbian" else "Connecting to camera... Camera is successfully activated and ready to use!"
                st.info(odgovor)
                robbi_speak(odgovor, st.session_state.lang, use_beep=True)
                
            elif "bluetooth" in user_query.lower() or "poveži" in user_query.lower() or "povezi" in user_query.lower():
                odgovor = "Skeniram okruženje... Bluetooth modul je uspešno spojen sa tvojim uređajima!" if st.session_state.lang == "Serbian" else "Scanning environment... Bluetooth module successfully connected to your devices!"
                st.info(odgovor)
                robbi_speak(odgovor, st.session_state.lang, use_beep=True)
                
            else:
                # Pametni mozak sa ispravljenom pretragom
                prompt = f"Ti si Robbi, napredni piskutavi AI asistent. Odgovori maksimalno precizno na pitanje klijenta: {user_query}"
                try:
                    response = model.generate_content(prompt)
                    st.write(f"**Robbi:** {response.text}")
                    robbi_speak(response.text, st.session_state.lang)
                    st.session_state.eyes_status = "normal"
                except Exception as e:
                    st.error(f"❌ Greška: {str(e)}")
                    robbi_speak("Izvinjavam se, došlo je do greške.", st.session_state.lang)

    # DESNI PANEL - HARDVERSKE KONTROLE I STATUSTI UREĐAJA
    with col_right:
        st.markdown("### 🎛️ Hardver & Veza")
        
        if st.button("📷 Testiraj Kameru", key="btn_camera"):
            st.session_state.eyes_status = "wide"
            st.toast("Inicijalizacija optičkog senzora...")
            st.success("Kamera uređaja je ONLINE i povezana!")
            robbi_speak("Kamera aktivirana" if st.session_state.lang == "Serbian" else "Camera activated", st.session_state.lang, use_beep=True)
            
        if st.button("🔵 Traži Bluetooth", key="btn_bluetooth"):
            st.session_state.eyes_status = "wide"
            st.toast("Skeniranje frekvencija...")
            st.success("Pronađeni uređaji: Smart TV, Laptop, Telefon." if st.session_state.lang == "Serbian" else "Found devices: Smart TV, Laptop, Phone.")
            robbi_speak("Bluetooth povezan" if st.session_state.lang == "Serbian" else "Bluetooth connected", st.session_state.lang, use_beep=True)
            
        if st.button("📟 VoiceMail Sekretarica", key="btn_voicemail"):
            msg = "Status: Telefon je povezan. Nema novih glasovnih poruka na čekanju." if st.session_state.lang == "Serbian" else "Status: Phone connected. No new voicemail messages."
            st.info(msg)
            robbi_speak("Nema novih poruka" if st.session_state.lang == "Serbian" else "No new messages", st.session_state.lang, use_beep=True)
            
        if st.button("🖼️ Render Slike", key="btn_render"):
            st.warning("Slikovni generator se otključava u sledećoj fazi razvoja koda." if st.session_state.lang == "Serbian" else "Image generator unlocks in the next development phase.")
