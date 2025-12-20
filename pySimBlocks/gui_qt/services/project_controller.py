import os
import shutil
from pySimBlocks.gui_qt.model.project_state import ProjectState
from pySimBlocks.gui_qt.services.yaml_tools import save_yaml
from pySimBlocks.project.generate_run_script import generate_python_content


class ProjectController:
    def __init__(self, project_state: ProjectState):
        self.project_state = project_state

    def save(self):
        save_yaml(self.project_state)

    def export(self):
        save_yaml(self.project_state)
        run_py = self.project_state.directory_path / "run.py"
        run_py.write_text(
            generate_python_content(
                model_yaml_path="model.yaml",
                parameters_yaml_path="parameters.yaml"
            )
        )

    def run(self):
        project_dir = self.project_state.directory_path
        if project_dir is None:
            return {}

        temp_dir = project_dir / ".temp"

        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)
        save_yaml(self.project_state, True)

        model_path = temp_dir / "model.yaml"
        param_path = temp_dir / "parameters.yaml"

        code = generate_python_content(
            model_yaml_path=str(model_path),
            parameters_yaml_path=str(param_path),
            enable_plots=False
        )

        old_cwd = os.getcwd()
        env = {}
        try:
            os.chdir(temp_dir)
            exec(code, env, env)
            logs = env.get("logs")
        except:
            logs = {}
        finally:
            os.chdir(old_cwd)

        return logs

    def can_plot(self):
        if not bool(self.project_state.logs):
            return False, "Simulation has not been done.\nPlease run fist."

        if not ("time" in self.project_state.logs):
            return False, "Time is not in logs."

        return True, "Plotting is available."
