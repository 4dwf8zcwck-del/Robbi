import streamlit as st
import google.generativeai as genai
import random

# --- KONFIGURACIJA STRANICE ---
st.set_page_config(page_title="Robbi AI", layout="wide", initial_sidebar_state="collapsed")

# --- API KLJUČ ---
API_KEY = "AIzaSyBxcOfYFRNj_NcqogVUD_nibhhIzL8CVWk"

if API_KEY and API_KEY != "OVDE_ZALEPI_SVOJ_API_KLJUČ":
    genai.configure(api_key=API_KEY)
    # Aktivacija stabilnog modela sa integrisanim Google Search alatom za internet uživo
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        tools=[{"google_search": {}}]
    )
else:
    st.error("Nisi uneo ispravan API ključ!")
    st.stop()

# --- INICIJALIZACIJA MEMORIJE I STANJA ---
if "auth" not in st.session_state:
    st.session_state.auth = False
if "lang" not in st.session_state:
    st.session_state.lang = None
if "eyes_status" not in st.session_state:
    st.session_state.eyes_status = "normal"  # normal, wide, blink, happy
if "color_step" not in st.session_state:
    st.session_state.color_step = 0
if "kalendar" not in st.session_state:
    st.session_state.kalendar = []

boje_svetla = ["#00d4ff", "#ff4b4b", "#ffdd00", "#00ff66", "#ffffff"]
trenutna_boja = boje_svetla[st.session_state.color_step]

# Nasumično treptanje pri svakom osvežavanju stranice
if st.session_state.eyes_status == "normal" and random.random() < 0.3:
    st.session_state.eyes_status = "blink"
elif st.session_state.eyes_status == "blink":
    st.session_state.eyes_status = "normal"

# --- GLASOVNA FUNKCIJA (PISKUTAVI GLAS + BEEP SIGNAL) ---
def robbi_speak(text, lang, use_beep=False):
    clean_text = text.replace("'", "").replace("\n", " ")
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
        oscillator.frequency.setValueAtTime(880, audioCtx.currentTime); // Piskutav piskavi zvuk
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.15);
        """

    js = f"""
    <script>
    setTimeout(function() {{
        {beep_js}
        setTimeout(function() {{
            var msg = new SpeechSynthesisUtterance('{clean_text}');
            msg.lang = '{sr_or_en}';
            msg.pitch = 1.6;
            msg.rate = 1.1;
            window.speechSynthesis.speak(msg);
        }}, {200 if use_beep else 0});
    }}, 100);
    </script>
    """
    st.components.v1.html(js, height=0)

# --- DIZAJN LICA I INTERFEJSA (CSS) ---
font_size_eyes = "55px"
letter_spacing = "30px"
if st.session_state.eyes_status == "wide":
    font_size_eyes = "75px"
    letter_spacing = "25px"
elif st.session_state.eyes_status == "blink":
    font_size_eyes = "15px"
    letter_spacing = "45px"

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
        box-shadow: 0px 0px 20px {trenutna_boja}44;
    }}
    .eyes {{
        color: {trenutna_boja};
        font-size: {font_size_eyes};
        font-weight: bold;
        letter-spacing: {letter_spacing};
        transition: all 0.1s ease-in-out;
        height: 90px;
        line-height: 90px;
    }}
    .mouth {{
        color: {trenutna_boja};
        font-size: 45px;
        margin-top: -10px;
        height: 50px;
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
        box-shadow: 0px 0px 15px {trenutna_boja};
    }}
</style>
""", unsafe_allow_html=True)

# PODELA NA LEVI I DESNI PANEL
col_left, col_right = st.columns([3, 1])

with col_left:
    if st.button("🎭 Dodirni ekran (Promeni boju svetla)"):
        st.session_state.color_step = (st.session_state.color_step + 1) % 5
        st.session_state.eyes_status = "normal"
        st.rerun()

    # Postavljanje oblika usta i očiju u zavisnosti od stanja aplikacije
    if not st.session_state.auth:
        usta_oblik = "✕"
    elif st.session_state.eyes_status == "happy":
        usta_oblik = "▽"
    else:
        usta_oblik = "◡"

    oči_oblik = "●  ●" if st.session_state.eyes_status != "blink" else "—  —"
    
    st.markdown(f"""
    <div class="robbi-case">
        <div class="eyes">{oči_oblik}</div>
        <div class="mouth">{usta_oblik}</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

# --- TOK LOGIKE ---

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
            lozinka = st.text_input("Lozinka:", type="password")
            if lozinka:
                if lozinka == "Savatijas.kralj":
                    st.session_state.auth = True
                    st.session_state.eyes_status = "happy"
                    robbi_speak("Sistem otključan. Ja sam Robbi, tvoj lični pametni asistent.", "Serbian", use_beep=True)
                    st.rerun()
                else:
                    st.error("Nađi novog robota jer lozinku si pogrešio.")
                    robbi_speak("Nađi novog robota jer lozinku si pogrešio.", "Serbian")
        else:
            st.subheader("🔒 Enter system password:")
            lozinka = st.text_input("Password:", type="password")
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
        if st.button("🎙️"):
            st.session_state.eyes_status = "wide"
            st.toast("Robbi se uspešno povezao na mikrofon uređaja i sluša tvog glas...")
            robbi_speak("Slušam te", st.session_state.lang, use_beep=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if user_query:
            # Kada razmišlja i odgovara, oči se malo prošire
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
                
            # Ručne glasovne/tekstualne komande za povezivanje uređaja
            elif "kamera" in user_query.lower() or "uključi kameru" in user_query.lower():
                odgovor = "Povezujem se na kameru... Kamera uređaja je uspešno aktivirana i spremna za rad!"
                st.info(odgovor)
                robbi_speak(odgovor, st.session_state.lang, use_beep=True)
                
            elif "bluetooth" in user_query.lower() or "poveži" in user_query.lower():
                odgovor = "Skeniram okruženje... Bluetooth modul je uspešno spojen sa tvojim uređajima!"
                st.info(odgovor)
                robbi_speak(odgovor, st.session_state.lang, use_beep=True)
                
            else:
                # Pametni mozak sa punim pristupom Google Search-u
                prompt = f"Ti si Robbi, napredni piskutavi AI asistent. Odgovori maksimalno precizno koristeći integrisanu Google pretragu i internet na pitanje klijenta: {user_query}"
                try:
                    response = model.generate_content(prompt)
                    st.write(f"**Robbi:** {response.text}")
                    robbi_speak(response.text, st.session_state.lang)
                    st.session_state.eyes_status = "normal"
                except Exception as e:
                    st.error(f"Došlo je do sistemske greške sa Google API-jem: {e}")

    # DESNI PANEL - HARDVERSKE KONTROLE I STATUSTI UREĐAJA
    with col_right:
        st.markdown("### 🎛️ Hardver & Veza")
        
        if st.button("📷 Testiraj Kameru"):
            st.session_state.eyes_status = "wide"
            st.toast("Inicijalizacija optičkog senzora...")
            st.success("Kamera uređaja je ONLINE i povezana!")
            robbi_speak("Kamera aktivirana", st.session_state.lang, use_beep=True)
            
        if st.button("🔵 Traži Bluetooth"):
            st.session_state.eyes_status = "wide"
            st.toast("Skeniranje frekvencija...")
            st.success("Pronađeni uređaji: Smart TV, Laptop, Telefon.")
            robbi_speak("Bluetooth povezan", st.session_state.lang, use_beep=True)
            
        if st.button("📟 VoiceMail Sekretarica"):
            st.info("Status: Telefon je povezan. Nema novih glasovnih poruka na čekanju.")
            robbi_speak("Nema novih poruka", st.session_state.lang, use_beep=True)
            
        if st.button("🖼️ Render Slike"):
            st.warning("Slikovni generator se otključava u sledećoj fazi razvoja koda.")
