import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as ep
import ndlib.models.opinions as op
import networkx as nx
import streamlit as st

MAX_NODES = 100
SEED = 42
MODELS = {
    "SI": ep.SIModel,
    "SIS": ep.SISModel,
    "SIR": ep.SIRModel,
    "Independent Cascades": ep.IndependentCascadesModel,
    "Voter": op.VoterModel,
    "QVoter": op.QVoterModel,
    "Sznajd": op.SznajdModel,
    "Deffuant": op.AlgorithmicBiasModel,
    "Algorithmic Bias": op.AlgorithmicBiasModel,
    "Hegselmann-Krause": op.HKModel,
}


def generate_synth_graph(model, num_nodes, **kwargs):
    """
    Generate a synthetic graph based on the given model and parameters
    :return: graph, pos
    """
    if model == "Erdos-Renyi":
        g = nx.erdos_renyi_graph(num_nodes, kwargs.get("p", 0.3), seed=SEED)
    elif model == "Barabasi-Albert":
        g = nx.barabasi_albert_graph(num_nodes, kwargs.get("m", 5), seed=SEED)
    elif model == "Watts-Strogatz":
        g = nx.watts_strogatz_graph(
            num_nodes, kwargs.get("k", 4), kwargs.get("p", 0.1), seed=SEED
        )
    elif model == "Mean Field":
        g = nx.complete_graph(num_nodes)
    else:
        raise ValueError(f"Unknown graph model: {model}")
    return g, nx.nx_agraph.pygraphviz_layout(g)


def handle_topology_parameters():
    """
    Allow the user to choose a graph model and specify model-specific parameters
    :return: graph_model, num_nodes, graph_parameters
    """
    # Allow the user to choose a graph model
    graph_model = st.selectbox(
        "Graph Model",
        ["Erdos-Renyi", "Barabasi-Albert", "Watts-Strogatz", "Mean Field"],
    )
    # Allow the user to specify the number of nodes
    num_nodes = st.slider(
        "Number of Nodes", min_value=10, max_value=MAX_NODES, value=50
    )

    # Display model-specific parameters
    if graph_model == "Erdos-Renyi":
        p_value = st.slider(
            "p (Probability of edge creation)", min_value=0.0, max_value=1.0, value=0.1
        )
        graph_parameters = {"p": p_value}
    elif graph_model == "Barabasi-Albert":
        m_value = st.slider(
            "m (Number of edges to attach from a new node)",
            min_value=1,
            max_value=10,
            value=3,
        )
        graph_parameters = {"m": m_value}
    elif graph_model == "Watts-Strogatz":
        k_value = st.slider(
            "k (Each node is connected to k nearest neighbors)",
            min_value=2,
            max_value=num_nodes,
            value=4,
        )
        p_value = st.slider(
            "p (Probability of rewiring each edge)",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
        )
        graph_parameters = {"k": k_value, "p": p_value}
    else:
        graph_parameters = {}

    return graph_model, num_nodes, graph_parameters


def handle_model_parameters():
    """
    Allow the user to choose a model type and specify model-specific parameters
    :return: model_method, model_config
    """
    # Allow the user to choose a model type
    model_type = st.radio("Model Type", ["epidemics", "opinions"], horizontal=True)
    fraction_infected = st.slider(
        "Fraction Infected", min_value=0.01, max_value=1.0, value=0.05
    )
    if model_type == "epidemics":
        model_method, config = __handle_epidemics_model_parameters()
    else:
        model_method, config = __handle_opinion_model_parameters()
    config.add_model_parameter("fraction_infected", fraction_infected)
    return model_method, config


def __handle_epidemics_model_parameters():
    model_type = st.selectbox("Model", ["SI", "SIS", "SIR", "Independent Cascades"])
    model_method = MODELS[model_type]
    config = mc.Configuration()
    if not model_type == "Independent Cascades":
        config.add_model_parameter(
            "beta",
            st.slider("beta (Infection rate)", min_value=0.0, max_value=1.0, value=0.1),
        )
    if model_type == "SIS":
        config.add_model_parameter(
            "lambda",
            st.slider(
                "lambda (Recovery rate)", min_value=0.0, max_value=1.0, value=0.1
            ),
        )
    elif model_type == "SIR":
        config.add_model_parameter(
            "gamma",
            st.slider("gamma (Removal rate)", min_value=0.0, max_value=1.0, value=0.1),
        )
    return model_method, config


def __handle_opinion_model_parameters():
    model_type = st.selectbox(
        "Model",
        [  # 'Voter', 'QVoter', 'Sznajd',
            "Deffuant",
            "Hegselmann-Krause",
            "Algorithmic Bias",
        ],
    )
    model_method = MODELS[model_type]
    config = mc.Configuration()
    config.add_model_parameter(
        "epsilon",
        st.slider(
            "epsilon (Bounded confidence threshold)",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
        ),
    )
    if model_type == "Algorithmic Bias":
        config.add_model_parameter(
            "gamma",
            st.slider("gamma (Algorithmic Bias)", min_value=1, max_value=100, value=1),
        )
    elif model_type == "Deffuant":
        config.add_model_parameter("gamma", 0)
    return model_method, config
