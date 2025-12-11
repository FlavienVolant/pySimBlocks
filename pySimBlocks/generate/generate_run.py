def generate_run(sim, plots):
    lines = []
    lines.append("import numpy as np")
    lines.append("import matplotlib.pyplot as plt")
    lines.append("from model import simulator, T, dt\n")

    # Logs
    log_list = sim.get("log", [])

    lines.append("logs = simulator.run(T=T, variables_to_log=[")

    for v in log_list:
        lines.append(f"    '{v}',")

    lines.append("])")
    lines.append("print('Simulation complete.')\n")

    lines.append("length = len(next(iter(logs.values())))")
    lines.append("time = np.array(logs['time'])\n")

    # Plots
    for fig in plots:
        title = fig["title"]
        vars_ = fig["log"]

        lines.append("plt.figure()")
        for var in vars_:
            safe = var.replace('.', '_')
            lines.append(f"{safe} = np.array(logs['{var}']).reshape(length, -1)")
            lines.append(f"for i in range({safe}.shape[1]):")
            lines.append(f"    plt.step(time, {safe}[:, i], where='post', label='{safe}'+str(i))")

        lines.append("plt.xlabel('Time [s]')")
        lines.append("plt.ylabel('Values')")
        lines.append(f"plt.title('{title}')")
        lines.append("plt.legend()")
        lines.append("plt.grid()")
        lines.append("")

    lines.append("plt.show()")

    return lines
