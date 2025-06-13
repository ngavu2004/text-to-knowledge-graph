from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import networkx as nx
import os
import colorsys
import tempfile
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo")

llm_transformer = LLMGraphTransformer(llm=llm)

async def extract_kg_from_text_chunk(chunk):
    document = Document(page_content=chunk)
    graph_document = await llm_transformer.aconvert_to_graph_documents([document])
    return graph_document[0].nodes, graph_document[0].relationships

async def extract_kg_from_text(text):
    """
    Extracts a knowledge graph from the provided text using GPT.
    
    Args:
        text (str): The input text from which to extract the knowledge graph.
        
    Returns:
        tuple: A tuple containing two lists - nodes and relationships.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = splitter.split_text(text)

    all_nodes = []
    all_relationships = []

    # Process each chunk separately
    for chunk in chunks:
        nodes, relationships = await extract_kg_from_text_chunk(chunk)
        all_nodes.extend(nodes)
        all_relationships.extend(relationships)

    # Deduplicate nodes and relationships
    all_nodes = [(n.id, n.type) for n in all_nodes]
    all_relationships = [(r.source.id, r.target.id, r.type) for r in all_relationships]

    return all_nodes, all_relationships

def parse_nodes(nodes):
    return [(node.id, node.type) for node in nodes]

def parse_relationships(relationships):
    return [(relationship.source.id, relationship.target.id, relationship.type) for relationship in relationships]

def generate_contrast_colors(n):
    """Generates n contrastive colors using HSV color space.

    Args:
        n: The number of colors to generate.

    Returns:
        A list of RGB color tuples.
    """
    colors = []
    for i in range(n):
        hue = i / n  # Evenly distribute hues
        saturation = 1.0 # Full saturation
        value = 1.0 # Full value
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        colors.append(rgb)
    return colors

def generate_color_map(node_types):
    """Generates a color map for the given node types.

    Args:
        node_types: A list of node types.

    Returns:
        A dictionary mapping each node type to a unique color.
    """
    colors = generate_contrast_colors(len(node_types))
    return dict(zip(node_types, colors))

def draw_kg_image(nodes, edges):
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes with type as an attribute
    for node_id, node_type in nodes:
        G.add_node(node_id, type=node_type)
        
    # Add edges with relationship type as a label
    for source, target, rel_type in edges:
        G.add_edge(source, target, label=rel_type)

    # Set up layout
    pos = nx.spring_layout(G, seed=42)

    # Draw nodes with different colors based on type
    node_colors = []
    color_map = generate_color_map([node[1]['type'] for node in G.nodes(data=True)])

    # Assign colors to nodes based on their type
    for node in G.nodes(data=True):
        node_type = node[1]['type']
        node_colors.append(color_map.get(node_type, 'gray'))

    # Draw the graph
    plt.figure(figsize=(12, 9))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='->', width=2)

    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=9)

    # Create custom legend handles
    legend_elements = [Patch(facecolor=color, label=node_type) for node_type, color in color_map.items()]
    img_path = tempfile.mktemp(suffix=".png")

    plt.title("Knowledge Graph", fontsize=15)
    plt.axis('off')
    plt.tight_layout()
    plt.legend(handles=legend_elements, title="Node Types")
    plt.savefig(img_path)
    plt.close()

    return img_path