from graphs.primary_assistant import part_4_graph

try:
    image = part_4_graph.get_graph(xray=True).draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(image)
except Exception as e:
    # This requires some extra dependencies and is optional
    print(f"Error: {e}")
