import time

import streamlit as st
from helpers import handle_topology_parameters, handle_model_parameters, generate_synth_graph
from diff2gif import Diff2GIF


def slow_type(t, placeholder):
    """type a string slowly in a placeholder"""
    for i in range(len(t)+1):
        placeholder.write(t[:i])
        time.sleep(.01)


st.title("Diff2GIF")
st.markdown("##### Create your own animated network visualization by exploiting a diffusion model!")
st.write(
    "Diff2GIF is a tool that allows you to create animated network visualizations by exploiting a diffusion model. "
    "Here you can choose a network topology and a diffusion model, and then generate a GIF animation of the resulting diffusion process."
    "\n This tool is based on the *NDLIB* Python library, which provides a high-level abstraction layer for "
    "modeling, simulating, and analyzing diffusion processes on complex networks."
    "\n For more information on the diffusion models, please refer to the [official documentation]("
    "https://ndlib.readthedocs.io/en/latest/index.html)"
    "")

col1, col2 = st.columns(2, gap='large')

with col1:
    st.subheader("Topology")
    graph_model, num_nodes, graph_parameters = handle_topology_parameters()

with col2:
    st.subheader("Model")
    model_method, model_config = handle_model_parameters()

n_iters = st.number_input("Number of iterations", min_value=10, max_value=100, value=30)
ms = st.number_input("Snapshot duration (in ms)", min_value=100, max_value=1000*3, value=1000)

if st.button("Run"):
    placeholder = st.empty()
    slow_type("Generating Network... :hourglass:", placeholder)
    graph, pos = generate_synth_graph(graph_model, num_nodes, **graph_parameters)
    slow_type("Running Model... :hourglass:", placeholder)
    model = model_method(graph)
    model.set_initial_status(model_config)


    class Params:
        model = model
        n_iters = n_iters
        pos = pos


    d2g = Diff2GIF(graph, Params)
    slow_type( "Generating GIF...(this may take a while :face_with_rolling_eyes:)", placeholder)
    d2g.make("generated.gif", ms)

    # display
    slow_type("Displaying GIF...:sunglasses:", placeholder)
    st.image("generated.gif")
    slow_type("Done! :tada: download your GIF below :point_down:", placeholder)
    # download
    with open('generated.gif', 'rb') as file:
        btn = st.download_button(
            label='Download GIF',
            data=file,
            mime='image/gif'
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
<p>Developed with ❤ by <a href="https://linktr.ee/andreafailla" target="_blank">Andrea Failla</a>.
<br>Powered by <img src="https://user-images.githubusercontent.com/7164864/217935870-c0bc60a3-6fc0-4047-b011-7b4c59488c91.png" style="width:40px;height:18px;"> 
and <img src="https://raw.githubusercontent.com/GiulioRossetti/ndlib/master/docs/ndlogo2.png" style="width:40px;height:18px;"></p>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)
