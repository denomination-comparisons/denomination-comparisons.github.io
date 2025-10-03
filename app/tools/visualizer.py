
import networkx as nx
import matplotlib.pyplot as plt
import re
import os
from uuid import uuid4

# Ensure matplotlib uses a non-interactive backend to avoid issues in a web server environment
plt.switch_backend('Agg')

def generate_concept_map(text_input: str, static_folder: str) -> str | None:
    """
    Generates a directed concept map from a structured text input and saves it
    to the static folder.

    Args:
        text_input (str): A string where each line defines a relationship,
                          formatted as "Source -> Target [Label]".
        static_folder (str): The absolute path to the static folder where the image will be saved.

    Returns:
        str | None: The filename of the generated map if successful, otherwise None.
    """
    G = nx.DiGraph()
    edge_labels = {}

    pattern = re.compile(r'(.+?)\s*->\s*(.+?)\s*\[(.+?)\]')

    for line in text_input.strip().split('\n'):
        match = pattern.match(line.strip())
        if match:
            source, target, label = [s.strip() for s in match.groups()]
            G.add_edge(source, target)
            edge_labels[(source, target)] = label

    if not G.nodes():
        print("No valid relationships found in the input.")
        return None

    plt.figure(figsize=(16, 12))
    pos = nx.spring_layout(G, k=0.9, iterations=50, seed=42)

    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='#a0c4ff', alpha=0.9)
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7, edge_color='#b1b1b1', arrowsize=20)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, font_color='#c9184a')

    plt.title('Concept Map', size=20)
    plt.axis('off')
    
    # Generate a unique filename to avoid browser caching issues
    filename = f"concept_map_{uuid4().hex}.png"
    output_path = os.path.join(static_folder, filename)

    try:
        plt.savefig(output_path, format='PNG', dpi=200, bbox_inches='tight')
        plt.close() # Free up memory
        print(f"Concept map saved successfully as '{output_path}'")
        return filename
    except Exception as e:
        print(f"Error saving file: {e}")
        plt.close()
        return None
