import os
import yaml
import streamlit as st
from pySimBlocks.api.helpers import FlowStyleList

def render_yaml_export(blocks, connections, dt, T, logs, plots):
    st.header("YAML Export")

    yaml_blocks = []
    for b in blocks:
        entry = {"name": b["name"], "from": b["from"], "type": b["type"]}

        # Add parameters EXCEPT empty ones
        for k, v in b["parameters"].items():

            # Skip empty strings
            if isinstance(v, str) and v.strip() == "":
                continue

            # Skip None
            if v is None:
                continue

            # If it's a list but empty → skip (optional)
            if isinstance(v, list) and len(v) == 0:
                continue

            # If parsed array (list of lists)
            if isinstance(v, list):
                if isinstance(v[0], list):
                    entry[k] = FlowStyleList([FlowStyleList(row) for row in v])
                else:
                    entry[k] = FlowStyleList(v)
            else:
                entry[k] = v

        yaml_blocks.append(entry)

    yaml_connections = [
        FlowStyleList([f"{s}.{sp}", f"{d}.{dp}"])
        for (s, sp, d, dp) in connections
    ]

    sim = {"dt": dt, "T": T}
    if logs:
        sim["log"] = logs

    yaml_data = {
        "blocks": yaml_blocks,
        "connections": yaml_connections,
        "simulation": sim
    }

    if plots:
        yaml_data["plot"] = [{"title": p["title"], "log": p["signals"]} for p in plots]

    yaml_str = yaml.dump(yaml_data, sort_keys=False)
    with st.expander("file content"):
        st.code(yaml_str, language="yaml")

    project_dir = st.session_state.get("project_dir", None)
    if not project_dir:
        st.error("Please set a project directory first.")
        return
    if st.button("Save project"):

        os.makedirs(project_dir, exist_ok=True)

        with open(os.path.join(project_dir, "project.yaml"), "w") as f:
            f.write(yaml.dump(yaml_data, sort_keys=False))

        st.success(f"Exported to {project_dir}")

    return yaml_data
