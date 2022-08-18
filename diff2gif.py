# graphs
import networkx as nx

# visualization
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

# io
import imageio
import os


class Diff2GIF:
    def __init__(self, g, params) -> None:

        self.g = g.copy()

        if params.model.initial_status is None:
            raise Exception(
                "The model is not configured. Use model.set_initial_status() to initialize your model."
            )

        self.model = params.model
        self.iterations = self.model.iteration_bunch(params.n_iters)

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
        if "edges" not in self.colors:
            self.colors["edges"] = "#999999"
        self.plot_params = {
            "pos": params.pos if hasattr(params, "pos") else nx.spring_layout(self.g),
            "alpha": params.alpha if hasattr(params, "alpha") else 0.8,
            "with_labels": params.with_labels
            if hasattr(params, "with_labels")
            else False,
            "width": params.width if hasattr(params, "width") else 0.1,
            "node_size": params.node_size if hasattr(params, "node_size") else 90,
        }
        self.status_dict = self.__get_status_dict()
        self.node_statuses = None
        self.filenames = []

    def make(self, fname: str, snap_duration: float = 0.2):
        """
        make _summary_

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
        for status, code in self.model.available_statuses.items():
            dic[str(code)] = {"status": status, "color": self.colors[status]}
        return dic

    def __draw_iteration(self, t, it):

        # assign status to each node
        if self.node_statuses is None:
            self.node_statuses = it["status"]
        else:
            self.node_statuses.update(it["status"])

        # plot network
        plt.title(f"Network state at t={t}")
        nx.draw(
            self.g,
            node_color=[
                self.status_dict[str(self.node_statuses[n])]["color"]
                for n in self.g.nodes()
            ],
            edge_color=self.colors["edges"],
            **self.plot_params,
        )

        # plot legend
        handles = []
        for _, col in self.status_dict.items():
            S = mlines.Line2D(
                [],
                [],
                color=col["color"],
                marker="o",
                alpha=self.plot_params["alpha"],
                markersize=10,
                linewidth=0,
                label=col["status"],
            )
            handles.append(S)

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
