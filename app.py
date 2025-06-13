import streamlit as st
import asyncio
from graph_functions import extract_kg_from_text, parse_nodes, parse_relationships, draw_kg_image

st.title("📘 Knowledge Graph Image Generator")
st.write("Paste any descriptive text below. This app uses GPT to extract a knowledge graph and render it as an image.")

text = st.text_area("📝 Paste your text here", height=300)

if st.button("🧠 Generate Knowledge Graph"):
    if not text:
        st.warning("Please provide text input.")
    else:
        with st.spinner("Processing with GPT..."):
            graph_nodes, graph_relationships = asyncio.run(extract_kg_from_text(text))

        st.subheader("📜 Raw GPT Output")
        st.code([graph_nodes, graph_relationships], language="python")

        try:
            nodes_part = parse_nodes(graph_nodes)
            relationships_part = parse_relationships(graph_relationships)

            if nodes_part and relationships_part:
                st.subheader("🖼️ Knowledge Graph Image")
                img_path = draw_kg_image(nodes_part, relationships_part)
                st.image(img_path, use_column_width=True)
            else:
                st.error("Could not parse graph structure from GPT response.")
        except Exception as e:
            st.error(f"Error parsing output: {e}")