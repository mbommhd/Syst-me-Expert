import streamlit as st 

# Configuration de la page
st.set_page_config(page_title="Système Expert d'Orientation-Faculté des Sciences de l'Université de Douala", page_icon="Logo FS", layout="wide")

# En-tete et présentation
st.title("Assistant d'Orientation Académique")
st.subheader("Faculté des Sciences-Université de Douala")
st.markdown("Bienvenue! Ce système vous aide à trouver la filière idéale (Bac / Bac+2) et à vérifier votre éligibilité.")
st.divider()

# Initialisation des états de session Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content":"Bonjour! Quel est votre niveau d'étude actuel (Bac / Bac+2) ?"}
    ]
    
# Zone d'affichage de la discussion
for message in st.session_state.messages:
    with st.chat_message(message["role"]):st.write(message["content"])
    
# Zone de saisie utilisateur et d'interaction
prompt = st.chat_input("Message")
if prompt:
    # Affichage immédiat du message utililateur
    st.session_state.messages.append({"role":"user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    # Zone de traitement (Emplacement où l'orchestrateur sera appelé après le merge)
    with st.chat_message("assistant"):
        with st.spinner("Analyse du profil en cours..."):
            # Simulation temporaire en attendant le merge
            réponse_bot = f"Message reçu: '{prompt}'. (L'orchestrateur répondra une fois connecté).)"
            st.write(réponse_bot)
            
    # Sauvegarde de la réponse su bot dans l'historique
    st.session_state.messages.append({"role":"assistant", "content":réponse_bot})