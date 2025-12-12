import streamlit as st
from pySimBlocks.generate.generate_parameters import generate_parameters
from pySimBlocks.generate.generate_model import generate_model
from pySimBlocks.generate.generate_run import generate_run


def generate_code(yaml_data):
    blocks = yaml_data["blocks"]
    connections = yaml_data["connections"]
    simulation = yaml_data["simulation"]
    plots = yaml_data.get("plot", [])

    param = "\n".join(generate_parameters(blocks, simulation))
    model = "\n".join(generate_model(blocks, connections))
    run   = "\n".join(generate_run(simulation, plots))

    st.session_state["generated_param"] = param
    st.session_state["generated_model"] = model
    st.session_state["generated_run"]   = run

    st.session_state["generated"] = True

def render_generated_code():
    param = st.session_state["generated_param"]
    model = st.session_state["generated_model"]
    run = st.session_state["generated_run"]

    st.header("Generated Python Files")

    with st.expander("parameters_auto.py"):
        st.code(param, language="python")

    with st.expander("model.py"):
        st.code(model, language="python")

    with st.expander("run.py"):
        st.code(run, language="python")
