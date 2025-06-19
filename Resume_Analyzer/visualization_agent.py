from uagents import Agent, Context, Model
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Address of the embedding agent
EMBEDDING_AGENT_ADDRESS = "agent1qdjckrv66ks5pm9g0mu8a2allgjyerxrwa7vmm5k6vgfy7f9rhq8u4l0t7f"

# Model for receiving similarity score
class SimilarityResponse(Model):
    extracted_text: str
    similarity: float

# Create Visualization Agent
visualization_agent = Agent(
    name="visualization_agent",
    port=5003,
    endpoint="http://localhost:5003/submit",
    seed="visualization_seed"
)

# Dictionary to store received similarity scores
similarity_scores = {}

@visualization_agent.on_message(model=SimilarityResponse)
async def handle_similarity(ctx: Context, sender: str, response: SimilarityResponse):
    ctx.logger.info(f"Received similarity score: {response.similarity} from {sender}")

    # Store the similarity score
    similarity_scores["Overall Match"] = response.similarity * 100  # Convert to percentage

    # Run the visualization
    visualize_results()

def visualize_results():
    """Visualize the similarity score using Streamlit and Plotly."""
    st.title("Resume Matching Visualization")

    if "Overall Match" in similarity_scores:
        results_df = [{"Resume Name": "Candidate 1", "Overall Match": similarity_scores["Overall Match"]}]

        # Bar chart for match scores
        fig = px.bar(
            results_df,
            x='Resume Name',
            y='Overall Match',
            title='Match Score Comparison',
            color='Overall Match',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Radar chart for different categories
        categories = ['Skills', 'Experience', 'Education', 'Domain', 'Certifications']
        values = [similarity_scores["Overall Match"] * 0.8,  # Example breakdown
                  similarity_scores["Overall Match"] * 0.7,
                  similarity_scores["Overall Match"] * 0.6,
                  similarity_scores["Overall Match"] * 0.75,
                  similarity_scores["Overall Match"] * 0.85]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Top Candidate'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title='Top Candidate Analysis'
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    visualization_agent.run()
