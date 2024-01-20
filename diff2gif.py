# graphs
import os

# io
import imageio
import matplotlib.lines as mlines
# visualization
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.colors import to_hex, to_rgb


def interpolate_color(color1, color2, t):
    """
    Interpolate between two colors.
    """
    res = []
    for i in range(3):
        res.append(int((1 - t) * color1[i] + t * color2[i]))

    return tuple(res)


def get_color_from_gradient(value, gradient):
    """
    Get the hex color from a color gradient based on a given value.
    """
    if not (0 <= value <= 1):
        raise ValueError("Value must be in the range [0, 1]")

    segments = len(gradient) - 1
    segment = int(value * segments)
    t = (value * segments) - segment

    color1 = (
        to_rgb(gradient[segment])
        if isinstance(gradient[segment], str)
        else gradient[segment]
    )
    color2 = (
        to_rgb(gradient[segment + 1])
        if isinstance(gradient[segment + 1], str)
        else gradient[segment + 1]
    )
    interpolated_color = interpolate_color(
        np.array(color1) * 255, np.array(color2) * 255, t
    )

    return to_hex(np.array(interpolated_color) / 255.0)


class Diff2GIF:
    def __init__(self, g, params) -> None:
        self.g = g.copy()

        if params.model.initial_status is None:
            raise Exception(
                "The model is not configured. Use model.set_initial_status() to initialize your model."
            )

        self.model = params.model
        self.model_type = str(type(self.model)).split(".")[2]
        self.iterations = self.model.iteration_bunch(params.n_iters)
        if self.model_type == "epidemics":
            self.colors = (
                params.colors
                if hasattr(params, "colors")
                else {
                    "Susceptible": "#377eb8",  # blue
                    "Infected": "#e41a1c",  # red
                    "Removed": "#4daf4a",  # green
                    "edges": "#999999",  # gray
                }
            )
        elif self.model_type == "opinions":
            self.colors = (
                params.colors
                if hasattr(params, "colors")
                else {
                    "0": "#000000",  # green
                    "1": "#ffffff",  # red
                }
            )

        if "edges" not in self.colors:
            self.colors["edges"] = "#999999"
        self.plot_params = {
            "pos": params.pos if hasattr(params, "pos") else nx.spring_layout(self.g),
            "alpha": params.alpha if hasattr(params, "alpha") else 0.8,
            "with_labels": params.with_labels
            if hasattr(params, "with_labels")
            else False,
            "width": params.width if hasattr(params, "width") else 0.5,
            "node_size": params.node_size if hasattr(params, "node_size") else 90,
        }
        self.status_dict = self.__get_status_dict()
        self.node_statuses = None
        self.filenames = []

    def make(self, fname: str, snap_duration: float = 0.2):
        """
        Make a gif from the simulation. The output file name must end in .gif.

        :param fname: desired output filename
        :type fname: str
        :param snap_duration: duration of a single snapshot in seconds, defaults to 0.2
        :type snap_duration: float, optional
        """
        assert fname.endswith(".gif"), "file name must end in .gif"
        self.__draw_all()
        images = list(map(lambda filename: imageio.imread(filename), self.filenames))
        imageio.mimsave(fname, images, duration=snap_duration)
        self.__clean()

    def __get_status_dict(self):
        dic = dict()
        if self.model_type == "epidemics":
            for status, code in self.model.available_statuses.items():
                dic[str(code)] = {"status": status, "color": self.colors[status]}

        elif self.model_type == "opinions":
            for n, status in self.model.status.items():
                status = round(status, 4)
                dic[str(status)] = {
                    "status": status,
                    "color": get_color_from_gradient(
                        status, [self.colors["0"], self.colors["1"]]
                    ),
                }

        return dic

    def __draw_iteration(self, t, it):
        # assign status to each node
        if self.node_statuses is None:
            self.node_statuses = it["status"]
        else:
            self.node_statuses.update(it["status"])

        # assign color to each node
        if self.model_type == "epidemics":
            node_colors = [
                self.status_dict[str(self.node_statuses[n])]["color"]
                for n in self.g.nodes()
            ]
        else:
            node_colors = [
                get_color_from_gradient(
                    self.node_statuses[n], [self.colors["0"], self.colors["1"]]
                )
                for n in self.g.nodes()
            ]

        # plot network
        plt.title(f"Network state at t={t}")
        nx.draw(
            self.g,
            node_color=node_colors,
            edge_color=self.colors["edges"],
            **self.plot_params,
        )

        # plot legend
        if self.model_type == "epidemics":
            handles = []
            for _, col in self.status_dict.items():
                zzz = mlines.Line2D(
                    [],
                    [],
                    color=col["color"],
                    marker="o",
                    alpha=self.plot_params["alpha"],
                    markersize=10,
                    linewidth=0,
                    label=col["status"],
                )
                handles.append(zzz)

            plt.legend(handles=handles, loc=0)

    def __draw_all(self):
        for t, it in enumerate(self.iterations):
            self.__draw_iteration(t, it)
            filename = f"t_{t}.png"
            plt.savefig(filename)
            plt.close()
            self.filenames.append(filename)

    def __clean(self):
        for filename in self.filenames:
            if os.path.isfile(filename):
                os.remove(filename)
        self.filenames = []
