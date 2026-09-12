"""
Generate SAVORIA architecture diagram using matplotlib.
Run: python docs/generate_architecture.py
"""

import sys
import os


def _create_svg_diagram():
    """Create an SVG architecture diagram."""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 720" width="900" height="720">
  <defs>
    <style>
      .title { font: bold 20px 'Segoe UI', sans-serif; fill: #2c2420; }
      .subtitle { font: 13px 'Segoe UI', sans-serif; fill: #6b5c52; }
      .box-label { font: bold 13px 'Segoe UI', sans-serif; fill: #2c2420; }
      .box-sublabel { font: 11px 'Segoe UI', sans-serif; fill: #6b5c52; }
      .section-label { font: bold 11px 'Segoe UI', sans-serif; fill: #9c8880; letter-spacing: 1px; }
      .arrow { stroke: #b5651d; stroke-width: 1.5; fill: none; marker-end: url(#arrowhead); }
    </style>
    <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="#b5651d"/>
    </marker>
  </defs>

  <!-- Background -->
  <rect width="900" height="720" fill="#faf8f5"/>
  
  <!-- Title -->
  <text x="450" y="38" class="title" text-anchor="middle">SAVORIA — System Architecture</text>
  <text x="450" y="58" class="subtitle" text-anchor="middle">AI-Powered RAG-Based Intelligent Recipe Preparation Agent</text>
  
  <!-- ─── USER ─── -->
  <rect x="370" y="80" width="160" height="44" rx="8" fill="#ffffff" stroke="#e8e0d5" stroke-width="1.5"/>
  <text x="450" y="100" class="box-label" text-anchor="middle">User</text>
  <text x="450" y="116" class="box-sublabel" text-anchor="middle">Ingredients + Preferences</text>
  <line x1="450" y1="124" x2="450" y2="148" class="arrow"/>
  
  <!-- ─── FRONTEND ─── -->
  <rect x="300" y="148" width="300" height="52" rx="8" fill="#fdf0e8" stroke="#d4894a" stroke-width="1.5"/>
  <text x="450" y="170" class="box-label" text-anchor="middle">SAVORIA Frontend</text>
  <text x="450" y="186" class="box-sublabel" text-anchor="middle">React 18 · React Router · Vite</text>
  <line x1="450" y1="200" x2="450" y2="224" class="arrow"/>
  
  <!-- ─── BACKEND / API ─── -->
  <rect x="300" y="224" width="300" height="52" rx="8" fill="#fdf0e8" stroke="#d4894a" stroke-width="1.5"/>
  <text x="450" y="246" class="box-label" text-anchor="middle">Backend API</text>
  <text x="450" y="262" class="box-sublabel" text-anchor="middle">FastAPI · Python 3.11 · Uvicorn</text>
  
  <!-- ─── AGENTIC LAYER ─── -->
  <rect x="60" y="310" width="780" height="130" rx="10" fill="#f5f1eb" stroke="#e8e0d5" stroke-width="1.5"/>
  <text x="80" y="330" class="section-label">AGENTIC WORKFLOW</text>

  <rect x="80" y="338" width="130" height="52" rx="6" fill="#ffffff" stroke="#e8e0d5"/>
  <text x="145" y="358" class="box-label" text-anchor="middle">Ingredient</text>
  <text x="145" y="372" class="box-label" text-anchor="middle">Analyzer</text>
  <text x="145" y="384" class="box-sublabel" text-anchor="middle">Normalise · Categorise</text>

  <rect x="230" y="338" width="130" height="52" rx="6" fill="#ffffff" stroke="#e8e0d5"/>
  <text x="295" y="358" class="box-label" text-anchor="middle">Preference</text>
  <text x="295" y="372" class="box-label" text-anchor="middle">Analyzer</text>
  <text x="295" y="384" class="box-sublabel" text-anchor="middle">Diet · Cuisine · Time</text>

  <rect x="380" y="338" width="130" height="52" rx="6" fill="#ffffff" stroke="#e8e0d5"/>
  <text x="445" y="358" class="box-label" text-anchor="middle">Substitution</text>
  <text x="445" y="372" class="box-label" text-anchor="middle">Advisor</text>
  <text x="445" y="384" class="box-sublabel" text-anchor="middle">Ingredient Swaps</text>

  <rect x="530" y="338" width="130" height="52" rx="6" fill="#ffffff" stroke="#e8e0d5"/>
  <text x="595" y="358" class="box-label" text-anchor="middle">Dietary</text>
  <text x="595" y="372" class="box-label" text-anchor="middle">Adapter</text>
  <text x="595" y="384" class="box-sublabel" text-anchor="middle">Vegan · GF · etc.</text>

  <rect x="680" y="338" width="140" height="52" rx="6" fill="#ffffff" stroke="#e8e0d5"/>
  <text x="750" y="358" class="box-label" text-anchor="middle">Recipe</text>
  <text x="750" y="372" class="box-label" text-anchor="middle">Planner</text>
  <text x="750" y="384" class="box-sublabel" text-anchor="middle">Orchestrates workflow</text>
  
  <!-- Arrow from Backend to agentic -->
  <line x1="450" y1="276" x2="450" y2="310" class="arrow"/>
  
  <!-- ─── RAG RETRIEVAL ─── -->
  <rect x="60" y="474" width="360" height="76" rx="10" fill="#edf4f0" stroke="#b8d9c4" stroke-width="1.5"/>
  <text x="80" y="496" class="section-label">RAG RETRIEVAL</text>
  <text x="240" y="520" class="box-label" text-anchor="middle">Recipe Knowledge Base + FAISS Index</text>
  <text x="240" y="536" class="box-sublabel" text-anchor="middle">sentence-transformers · all-MiniLM-L6-v2 · Top-K Cosine Similarity</text>

  <!-- ─── IBM WATSONX ─── -->
  <rect x="460" y="474" width="380" height="76" rx="10" fill="#eef4fb" stroke="#b8d4ef" stroke-width="1.5"/>
  <text x="480" y="496" class="section-label">AI GENERATION</text>
  <text x="650" y="520" class="box-label" text-anchor="middle">IBM watsonx.ai</text>
  <text x="650" y="536" class="box-sublabel" text-anchor="middle">Meta LLaMA 3.3 70B · RAG-augmented prompt · JSON output</text>

  <!-- Arrows to RAG and WatsonX -->
  <line x1="300" y1="440" x2="240" y2="474" class="arrow"/>
  <line x1="600" y1="440" x2="650" y2="474" class="arrow"/>
  
  <!-- ─── RECIPE OUTPUT ─── -->
  <rect x="300" y="588" width="300" height="52" rx="8" fill="#fdf0e8" stroke="#d4894a" stroke-width="1.5"/>
  <text x="450" y="610" class="box-label" text-anchor="middle">Personalised Recipes</text>
  <text x="450" y="626" class="box-sublabel" text-anchor="middle">Substitutions · Dietary Adaptation · Steps</text>
  
  <!-- Arrows back from RAG and WatsonX to recipe output -->
  <line x1="240" y1="550" x2="380" y2="588" class="arrow"/>
  <line x1="650" y1="550" x2="520" y2="588" class="arrow"/>
  
  <!-- ─── COOKING MODE / SAVED ─── -->
  <rect x="170" y="672" width="200" height="40" rx="8" fill="#ffffff" stroke="#e8e0d5"/>
  <text x="270" y="692" class="box-label" text-anchor="middle">Cooking Mode</text>
  <text x="270" y="705" class="box-sublabel" text-anchor="middle">Step-by-step · Progress</text>
  
  <rect x="530" y="672" width="200" height="40" rx="8" fill="#ffffff" stroke="#e8e0d5"/>
  <text x="630" y="692" class="box-label" text-anchor="middle">Saved / Recent</text>
  <text x="630" y="705" class="box-sublabel" text-anchor="middle">localStorage · Session</text>
  
  <line x1="380" y1="640" x2="270" y2="672" class="arrow"/>
  <line x1="520" y1="640" x2="630" y2="672" class="arrow"/>
</svg>'''

    with open("docs/architecture.svg", "w") as f:
        f.write(svg)
    print("SVG architecture diagram saved to docs/architecture.svg")


def create_matplotlib_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(14, 11))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.axis('off')
    fig.patch.set_facecolor('#faf8f5')

    def box(x, y, w, h, label, sublabel='', color='#ffffff', border='#e8e0d5', fontsize=10):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                               facecolor=color, edgecolor=border, linewidth=1.5)
        ax.add_patch(rect)
        if sublabel:
            ax.text(x + w/2, y + h*0.62, label, ha='center', va='center',
                    fontsize=fontsize, fontweight='bold', color='#2c2420')
            ax.text(x + w/2, y + h*0.28, sublabel, ha='center', va='center',
                    fontsize=8, color='#6b5c52')
        else:
            ax.text(x + w/2, y + h/2, label, ha='center', va='center',
                    fontsize=fontsize, fontweight='bold', color='#2c2420')

    def arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#b5651d', lw=1.5))

    # Title
    ax.text(7, 10.5, 'SAVORIA — System Architecture', ha='center', va='center',
            fontsize=16, fontweight='bold', color='#2c2420')
    ax.text(7, 10.15, 'AI-Powered RAG-Based Intelligent Recipe Preparation Agent',
            ha='center', va='center', fontsize=10, color='#6b5c52')

    # User
    box(5.5, 9.2, 3, 0.7, 'User', 'Ingredients + Preferences', '#ffffff', '#e8e0d5')
    arrow(7, 9.2, 7, 8.65)

    # Frontend
    box(4.5, 8.1, 5, 0.8, 'SAVORIA Frontend', 'React 18  ·  React Router  ·  Vite', '#fdf0e8', '#d4894a')
    arrow(7, 8.1, 7, 7.55)

    # Backend
    box(4.5, 7.0, 5, 0.8, 'Backend API', 'FastAPI  ·  Python 3.11  ·  Uvicorn', '#fdf0e8', '#d4894a')
    arrow(7, 7.0, 7, 6.5)

    # Agentic layer background
    bg = FancyBboxPatch((0.3, 5.3), 13.4, 1.0, boxstyle="round,pad=0.1",
                         facecolor='#f5f1eb', edgecolor='#e8e0d5', linewidth=1)
    ax.add_patch(bg)
    ax.text(0.5, 6.22, 'AGENTIC WORKFLOW', fontsize=8, fontweight='bold',
            color='#9c8880', letterspacing=1)

    agent_boxes = [
        (0.4, 5.35, 2.4, 'Ingredient\nAnalyzer', 'Normalise · Categorise'),
        (3.0, 5.35, 2.4, 'Preference\nAnalyzer', 'Diet · Cuisine · Time'),
        (5.6, 5.35, 2.4, 'Substitution\nAdvisor', 'Ingredient Swaps'),
        (8.2, 5.35, 2.4, 'Dietary\nAdapter', 'Vegan · GF · etc.'),
        (10.8, 5.35, 2.9, 'Recipe\nPlanner', 'Orchestrates'),
    ]
    for (bx, by, bw, bl, bs) in agent_boxes:
        box(bx, by, bw, 0.9, bl, bs, '#ffffff', '#e8e0d5', 9)

    arrow(7, 5.3, 7, 4.95)

    # RAG
    rag_bg = FancyBboxPatch((0.3, 3.8), 6.2, 1.0, boxstyle="round,pad=0.1",
                             facecolor='#edf4f0', edgecolor='#b8d9c4', linewidth=1.5)
    ax.add_patch(rag_bg)
    ax.text(0.5, 4.73, 'RAG RETRIEVAL', fontsize=8, fontweight='bold', color='#4a7c59')
    ax.text(3.4, 4.48, 'Recipe Knowledge Base + FAISS Index', ha='center', va='center',
            fontsize=9.5, fontweight='bold', color='#2c2420')
    ax.text(3.4, 4.1, 'sentence-transformers · all-MiniLM-L6-v2\nTop-K Cosine Similarity Retrieval',
            ha='center', va='center', fontsize=7.5, color='#6b5c52')
    arrow(3.4, 3.8, 3.4, 3.25)

    # IBM watsonx
    ibm_bg = FancyBboxPatch((7.0, 3.8), 6.7, 1.0, boxstyle="round,pad=0.1",
                              facecolor='#eef4fb', edgecolor='#b8d4ef', linewidth=1.5)
    ax.add_patch(ibm_bg)
    ax.text(7.2, 4.73, 'AI GENERATION', fontsize=8, fontweight='bold', color='#2d6da3')
    ax.text(10.35, 4.48, 'IBM watsonx.ai', ha='center', va='center',
            fontsize=9.5, fontweight='bold', color='#2c2420')
    ax.text(10.35, 4.1, 'Meta LLaMA 3.3 70B Instruct\nRAG-augmented prompt · JSON output',
            ha='center', va='center', fontsize=7.5, color='#6b5c52')
    arrow(10.35, 3.8, 10.35, 3.25)

    # Recipe output
    box(4.5, 2.5, 5, 0.8, 'Personalised Recipes', 'Substitutions · Dietary Adaptation · Step-by-step', '#fdf0e8', '#d4894a')
    arrow(3.4, 3.25, 5.5, 3.3)
    arrow(10.35, 3.25, 8.5, 3.3)
    arrow(7, 2.5, 7, 1.95)

    # Output panels
    box(1.5, 1.2, 3.5, 0.8, 'Cooking Mode', 'Step-by-step · Progress tracking')
    box(9.0, 1.2, 3.5, 0.8, 'Saved / Recent', 'localStorage · Session state')
    arrow(6.0, 2.15, 3.25, 2.0)
    arrow(8.0, 2.15, 10.75, 2.0)

    plt.tight_layout(pad=0.5)
    plt.savefig('docs/architecture.png', dpi=180, bbox_inches='tight',
                facecolor='#faf8f5', format='png')
    print("Architecture diagram saved to docs/architecture.png")
    plt.close()


if __name__ == '__main__':
    os.makedirs('docs', exist_ok=True)
    try:
        create_matplotlib_diagram()
    except Exception as e:
        print(f"matplotlib failed ({e}); creating SVG diagram")
        _create_svg_diagram()
