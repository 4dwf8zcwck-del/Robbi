import streamlit as st
import google.generativeai as genai
import time

# --- KONFIGURACIJA STRANICE ---
st.set_page_config(page_title="Robbi AI", layout="wide", initial_sidebar_state="collapsed")

# --- API KLJUČ ---
# OVDE UMESTO AIza... STAVI SVOJ KLJUČ I OBAVEZNO OSTAVI NAVODNIKE!
API_KEY = "AIzaSyAf3zIiLRb3Y-vwvuVl7zwAhtNu1dUafxY"

if API_KEY != "OVDE_ZALEPI_SVOJ_API_KLJUČ":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("Nisi uneo API ključ!")
    st.stop()

# --- INICIJALIZACIJA MEMORIJE, JEZIKA I RASPOREDA ---
if "auth" not in st.session_state:
    st.session_state.auth = False
if "lang" not in st.session_state:
    st.session_state.lang = None
if "eyes_wide" not in st.session_state:
    st.session_state.eyes_wide = False
if "color_step" not in st.session_state:
    st.session_state.color_step = 0
if "kalendar" not in st.session_state:
    st.session_state.kalendar = []

boje_svetla = ["#00d4ff", "#ff4b4b", "#ffdd00", "#00ff66", "#ffffff"]
trenutna_boja = boje_svetla[st.session_state.color_step]

# --- GLASOVNA FUNKCIJA (PISKUTAVI ROBOTSKI GLAS) ---
def robbi_speak(text, lang):
    clean_text = text.replace("'", "").replace("\n", " ")
    sr_or_en = 'sr-RS' if lang == "Serbian" else 'en-US'
    js = f"""
    <script>
    var msg = new SpeechSynthesisUtterance('{clean_text}');
    msg.lang = '{sr_or_en}';
    msg.pitch = 1.6;
    msg.rate = 1.1;
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js, height=0)

# --- DIZAJN I INTERFEJS (CSS) ---
st.markdown(f"""
<style>
    .robbi-case {{
        background-color: #120a21;
        border-radius: 40px;
        padding: 30px;
        text-align: center;
        border: 8px solid {trenutna_boja};
        width: 280px;
        margin: 0 auto;
    }}
    .eyes {{
        color: {trenutna_boja};
        font-size: {"75px" if st.session_state.eyes_wide else "55px"};
        font-weight: bold;
        letter-spacing: 30px;
        transition: all 0.2s ease;
    }}
    .mouth {{
        color: {trenutna_boja};
        font-size: 45px;
        margin-top: -10px;
    }}
    .stButton>button {{
        width: 100%;
        background-color: #1f143a;
        color: white;
        border: 2px solid {trenutna_boja};
        border-radius: 10px;
    }}
    .mic-btn>button {{
        background-color: {trenutna_boja} !important;
        color: black !important;
        font-size: 30px !important;
        border-radius: 50% !important;
        width: 80px !important;
        height: 80px !important;
        margin: 0 auto !important;
        display: block !important;
    }}
</style>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([3, 1])

with col_left:
    if st.button("🎭 Dodirni ekran / Promeni boju"):
        st.session_state.color_step = (st.session_state.color_step + 1) % 5
        st.rerun()

    usta_oblik = "✕" if not st.session_state.auth else "◡"
    st.markdown(f"""
    <div class="robbi-case">
        <div class="eyes">● ●</div>
        <div class="mouth">{usta_oblik}</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

# --- LOGIKA ---
if st.session_state.lang is None:
    with col_left:
        st.subheader("Select Language / Izaberi Jezik")
        c1, c2 = st.columns(2)
        if c1.button("English"):
            st.session_state.lang = "English"
            robbi_speak("Hello!", "English")
            st.rerun()
        if c2.button("Serbian"):
            st.session_state.lang = "Serbian"
            robbi_speak("Zdravo!", "Serbian")
            st.rerun()

elif not st.session_state.auth:
    with col_left:
        if st.session_state.lang == "Serbian":
            st.subheader("Zdravo! Unesi lozinku:")
            lozinka = st.text_input("Lozinka:", type="password")
            if lozinka:
                if lozinka == "Savatijas.kralj":
                    st.session_state.auth = True
                    robbi_speak("Otključano. Ja sam Robbi, tvoj asistent.", "Serbian")
                    st.rerun()
                else:
                    st.error("Nađi novog robota jer lozinku si pogrešio.")
                    robbi_speak("Nađi novog robota jer lozinku si pogrešio.", "Serbian")
        else:
            st.subheader("Hello! Enter password:")
            lozinka = st.text_input("Password:", type="password")
            if lozinka:
                if lozinka == "Savatijas.kralj":
                    st.session_state.auth = True
                    robbi_speak("Unlocked. I am Robbi, your assistant.", "English")
                    st.rerun()
                else:
                    st.error("Find a new robot because you got the password wrong.")
                    robbi_speak("Find a new robot because you got the password wrong.", "English")

else:
    with col_left:
        st.markdown("### 📅 Robbi Kalendar i Raspored")
        if st.session_state.kalendar:
            for i, dogadjaj in enumerate(st.session_state.kalendar, 1):
                st.write(f"{i}. 📌 {dogadjaj}")
        else:
            st.write("_Raspored je prazan. Reci mi preko mikrofona šta da zakažem._")
        
        user_query = st.chat_input("Pitaj Robbi-ja ili zakaži obavezu...")
        
        st.markdown('<div class="mic-btn">', unsafe_allow_html=True)
        if st.button("🎙️"):
            st.session_state.eyes_wide = True
            st.toast("Robbi se povezuje na mikrofon uređaja i sluša...")
        st.markdown('</div>', unsafe_allow_html=True)

        if user_query:
            st.session_state.eyes_wide = True
            
            if "podseti me" in user_query.lower() or "zakaži" in user_query.lower() or "zakazi" in user_query.lower():
                st.session_state.kalendar.append(user_query)
                odgovor = "U redu, zapisao sam u tvoj raspored!" if st.session_state.lang == "Serbian" else "Alright, I have added it to your schedule!"
                st.write(f"**Robbi:** {odgovor}")
                robbi_speak(odgovor, st.session_state.lang)
                st.rerun()
                
            elif "obriši kalendar" in user_query.lower() or "obrisi kalendar" in user_query.lower():
                st.session_state.kalendar = []
                odgovor = "Kalendar je uspešno obrisan." if st.session_state.lang == "Serbian" else "Calendar cleared."
                st.write(f"**Robbi:** {odgovor}")
                robbi_speak(odgovor, st.session_state.lang)
                st.rerun()
                
            else:
                prompt = f"Ti si Robbi, napredni piskutavi AI asistent. Odgovori maksimalno dobro i precizno koristeći internet, Google i Wikipediju na pitanje: {user_query}"
                response = model.generate_content(prompt)
                st.write(f"**Robbi:** {response.text}")
                robbi_speak(response.text, st.session_state.lang)

    with col_right:
        st.markdown("### 🎛️ Robbi Kontrole")
        if st.button("📷 Kamera"):
            st.toast("Povezivanje na kameru uređaja...")
            st.info("Kamera aktivna. Spremna za prepoznavanje u drugom delu.")
        if st.button("🔵 Bluetooth"):
            st.toast("Skeniranje Bluetooth okruženja...")
            st.info("Povezivanje na TV, Laptop, Telefon ili Robotsko telo...")
        if st.button("🖼️ Generiši Sliku"):
            st.info("Otključava se u drugom delu.")
        if st.button("📟 VoiceMail"):
            st.info("Sekretarica: Nema poruka.")
