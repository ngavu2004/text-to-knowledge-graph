import streamlit as st
import asyncio
from graph_functions import extract_kg_from_text, parse_nodes, parse_relationships, draw_kg_image
from file_functions import extract_text

st.title("📘 Knowledge Graph Image Generator")
st.write("Paste any descriptive text below. This app uses GPT to extract a knowledge graph and render it as an image.")

st.subheader("📂 Upload a File (PDF or TXT)")
text_present = st.session_state.get("manual_text", "").strip() != ""
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"], disabled=text_present, key="file_upload")

st.subheader("📝 Or Paste Text Manually")
manual_text = st.text_area("Paste your text below", height=200, disabled=uploaded_file is not None, key="manual_text")

text = ""
if uploaded_file:
    text = extract_text(uploaded_file)
elif manual_text.strip():
    text = manual_text.strip()

if st.button("🧠 Generate Knowledge Graph"):
    if not text:
        st.warning("Please provide text input.")
    else:
        nodes_part, relationships_part = [], []
        with st.spinner("Processing with GPT..."):
            nodes_part, relationships_part = asyncio.run(extract_kg_from_text(text))

        st.subheader("📜 Raw GPT Output")
        st.code([nodes_part, relationships_part], language="python")

        try:
            if nodes_part and relationships_part:
                st.subheader("🖼️ Knowledge Graph Image")
                img_path = draw_kg_image(nodes_part, relationships_part)
                st.image(img_path, use_column_width=True)
            else:
                st.error("Could not parse graph structure from GPT response.")
        except Exception as e:
            st.error(f"Error parsing output: {e}")