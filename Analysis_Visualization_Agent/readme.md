![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:automation](https://img.shields.io/badge/automation-3D8BD3)

# Resume Matching Visualization Agent

## Overview
This project implements a **Resume Matching Visualization Agent** using the `uagents` framework. The agent receives similarity scores from an embedding agent, processes them, and visualizes the results using **Streamlit** and **Plotly**.

## Features
- **Receives similarity scores** from an embedding agent.
- **Stores similarity scores** and converts them into percentage values.
- **Visualizes results** using interactive bar charts and radar charts.
- **Displays candidate analysis** based on multiple categories (Skills, Experience, Education, etc.).

## Technologies Used
- `uagents` for decentralized agent-based communication.
- `Streamlit` for UI visualization.
- `Plotly` for interactive charts.

## Installation & Setup
### Prerequisites
Ensure you have Python installed along with the required dependencies:

```bash
pip install uagents streamlit plotly
```

### Running the Agent
Run the visualization agent using:

```bash
python visualization_agent.py
```

## How It Works
1. The **Visualization Agent** listens for similarity scores from the embedding agent.
2. When a similarity score is received, it is stored and converted into a percentage.
3. The **Streamlit interface** displays:
   - **A bar chart** showing the overall match percentage.
   - **A radar chart** analyzing the candidate's performance across multiple criteria.
4. The agent runs locally and interacts via `http://localhost:5003/submit`.

## Code Breakdown
### **Similarity Response Model**
Defines the structure for the received similarity score:
```python
class SimilarityResponse(Model):
    extracted_text: str
    similarity: float
```

### **Agent Initialization**
The agent listens on port `5003` and processes similarity scores:
```python
visualization_agent = Agent(
    name="visualization_agent",
    port=5003,
    endpoint="http://localhost:5003/submit",
    seed="visualization_seed"
)
```

### **Handling Similarity Scores**
On receiving a message, the similarity score is stored and processed:
```python
@visualization_agent.on_message(model=SimilarityResponse)
async def handle_similarity(ctx: Context, sender: str, response: SimilarityResponse):
    similarity_scores["Overall Match"] = response.similarity * 100
    visualize_results()
```

### **Visualization Using Streamlit & Plotly**
- **Bar Chart** for similarity scores:
```python
fig = px.bar(
    results_df,
    x='Resume Name',
    y='Overall Match',
    title='Match Score Comparison',
    color='Overall Match',
    color_continuous_scale='Blues'
)
st.plotly_chart(fig, use_container_width=True)
```
- **Radar Chart** for category analysis:
```python
fig.add_trace(go.Scatterpolar(
    r=values,
    theta=categories,
    fill='toself',
    name='Top Candidate'
))
st.plotly_chart(fig, use_container_width=True)
```

## Future Enhancements
- Support for multiple candidates.
- Integration with additional resume analysis metrics.
- Enhanced UI/UX improvements.

## Developer
Aishwarya