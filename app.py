import streamlit as st
from helpers import handle_topology_parameters, handle_model_parameters, generate_random_graph
from diff2gif import Diff2GIF
import imageio

st.title("Diff2GIF")
st.markdown("##### Create your own animated network visualization by exploiting a diffusion model!")
st.write(
    "Diff2GIF is a tool that allows you to create animated network visualizations by exploiting a diffusion model. "
    "The tool is based on the [NDLIB]() Python library, which provides a high-level abstraction layer for "
    "modeling, simulating, and analyzing diffusion processes on complex networks.")

col1, col2 = st.columns(2, gap='large')

with col1:
    st.subheader("Topology")
    graph_model, num_nodes, graph_parameters = handle_topology_parameters()

with col2:
    st.subheader("Model")
    model_method, model_config = handle_model_parameters()

n_iters = st.number_input("Number of iterations", min_value=10, max_value=100, value=10)
s = st.number_input("Snapshot duration (in s)", min_value=0., max_value=3., value=.3)

if st.button("Run"):
    st.write("Generating Network...")
    graph, pos = generate_random_graph(graph_model, num_nodes, **graph_parameters)
    st.write("Running Model...")
    model = model_method(graph)
    model.set_initial_status(model_config)
    model.iteration_bunch(n_iters)
    st.write("Generating GIF...")

    # display

    # download
    st.download_button(
        label="Download GIF",
        data= ,
        file_name="generated.gif",
        mime="image/gif",
    )
footer = """<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤ by <a style='display: block; text-align: center;' href="https://linktr.ee/andreafailla" target="_blank">Andrea Failla</a></p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
