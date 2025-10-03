
import networkx as nx
import matplotlib.pyplot as plt
import re

def generate_concept_map(text_input: str, output_filename: str = 'concept_map.png'):
    """
    Generates a directed concept map from a structured text input.

    Args:
        text_input (str): A string where each line defines a relationship,
                          formatted as "Source Concept -> Target Concept [Relationship Label]".
        output_filename (str): The name of the file to save the image to.
    """
    G = nx.DiGraph()
    edge_labels = {}

    # Regex to parse "Source -> Target [Label]"
    pattern = re.compile(r'(.+?)\s*->\s*(.+?)\s*\[(.+?)\]')

    for line in text_input.strip().split('\n'):
        match = pattern.match(line.strip())
        if match:
            source, target, label = match.groups()
            source = source.strip()
            target = target.strip()
            label = label.strip()
            
            G.add_edge(source, target)
            edge_labels[(source, target)] = label

    if not G.nodes():
        print("No valid relationships found in the input. Cannot generate map.")
        return

    # --- Visualization ---
    plt.figure(figsize=(14, 10))
    
    # Use a layout that spreads nodes out
    pos = nx.spring_layout(G, k=0.8, iterations=50, seed=42)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=3500, node_color='skyblue', alpha=0.9)

    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.7, edge_color='gray', arrowsize=20)

    # Draw node labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')

    # Draw edge labels
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, font_color='red')

    plt.title('Theological Concept Map', size=18)
    plt.axis('off') # Hide the axes
    
    try:
        plt.savefig(output_filename, format='PNG', dpi=300)
        print(f"Concept map saved successfully as '{output_filename}'")
    except Exception as e:
        print(f"Error saving file: {e}")

    plt.show()


# --- Example Usage ---
# Students would provide this text based on their research.
# This example compares concepts of covenant in Judaism and Christianity.
student_input = """
Gud -> Abraham [Sluter förbund med]
Abraham -> Isak [Fader till]
Gud -> Mose [Ger lagen till]
Mose -> Israeliterna [Leder]
Israeliterna -> Förbundet [Mottar]
Jesus -> Lärjungarna [Instiftar nytt förbund med]
Lärjungarna -> Världen [Sprider budskapet till]
Förbundet -> Jesus [Uppfylls i]
"""

if __name__ == '__main__':
    print("Generating example concept map...")
    generate_concept_map(student_input, 'theological_comparison_map.png')
