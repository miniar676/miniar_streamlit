import streamlit as st
import json
from langchain_community.llms import Ollama

# ======================================
# CONFIGURATION
# ======================================
DATASET_PATH = "C:/Users/MSI/Desktop/translation/partie1.jsonl"

# ======================================
# FONCTIONS
# ======================================
def find_person_by_query(query_value, query_field="id"):
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            if data.get("id") == query_value or data.get("caption") == query_value:
                yield data
                continue
            properties = data.get("properties", {})
            for field in ("name", "alias"):
                values = properties.get(field, [])
                if query_value in values:
                    yield data
                    break

def generate_person_report(person_obj):
    llm = Ollama(model="mistral")
    prompt = (
        "Voici la fiche JSON d'une personne extraite d'une base de données :\n"
        f"{json.dumps(person_obj, ensure_ascii=False, indent=2)}\n\n"
        "En te basant uniquement sur ces données, résume de manière claire et concise :\n"
        "- Le nom complet\n- L'identité/nationalité et genre\n"
        "- Les positions institutionnelles occupées (avec dates si possible)\n"
        "- Autres informations pertinentes (alias, email, etc)\n"
        "(Fais ta réponse en français.)"
    )
    return llm.invoke(prompt)

# ======================================
# CSS DESIGN PREMIUM
# ======================================
st.set_page_config(page_title="Résumé JSON ✨", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Open Sans', sans-serif;
        background-color: #f3f6fb;
    }

    .block-container {
        padding: 3rem 2rem;
        border-radius: 15px;
        background-color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin: 2rem;
    }

    .title-main {
        text-align: center;
        font-size: 40px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }

    .subtitle-main {
        text-align: center;
        font-size: 18px;
        color: #7f8c8d;
        margin-bottom: 2rem;
    }

    .stButton>button {
        background-color: #1abc9c;
        color: white;
        border-radius: 8px;
        padding: 0.6em 1.5em;
        border: none;
        font-weight: bold;
        font-size: 16px;
        transition: 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #16a085;
        transform: scale(1.05);
    }

    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 0.5rem;
        background-color: #f4f6fa;
        border: 1px solid #ccc;
    }
    </style>
""", unsafe_allow_html=True)

# ======================================
# INITIALISATION
# ======================================
if "person_data" not in st.session_state:
    st.session_state.person_data = None
if "summary" not in st.session_state:
    st.session_state.summary = None

# ======================================
# TITRE
# ======================================
st.markdown("<div class='title-main'>🧠 Générateur de Résumés LLM</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-main'>Entrez un identifiant, nom ou alias pour rechercher une personne</div>", unsafe_allow_html=True)

# ======================================
# RECHERCHE
# ======================================
col1, col2 = st.columns([5, 1])
with col1:
    query_input = st.text_input(
        "Recherchez par ID, nom ou alias",
        placeholder="Ex: 12345, Jean Dupont, أبو خالد...",
        label_visibility="collapsed"
    )
with col2:
    search_clicked = st.button("🔍 Rechercher")

if search_clicked and query_input.strip():
    query = query_input.strip()
    results = list(find_person_by_query(query))
    
    if not results:
        st.warning("❗ Aucune correspondance trouvée.")
        st.session_state.person_data = None
        st.session_state.summary = None
    else:
        person = results[0]
        st.session_state.person_data = person
        st.session_state.summary = None

# ======================================
# AFFICHAGE DONNÉES + BOUTON RÉSUMÉ
# ======================================
if st.session_state.person_data:
    st.success("✅ Personne trouvée. Affichage de la fiche.")
    
    with st.expander("📄 Données JSON complètes"):
        st.json(st.session_state.person_data)

    if st.button("✨ Générer un résumé LLM"):
        with st.spinner("⏳ Génération du résumé avec Mistral..."):
            summary = generate_person_report(st.session_state.person_data)
            st.session_state.summary = summary

# ======================================
# AFFICHAGE DU RÉSUMÉ CLASSIQUE
# ======================================
if st.session_state.summary:
    st.markdown("### 📝 Résumé généré :")
    st.write(st.session_state.summary)
