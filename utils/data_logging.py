from dataclasses import dataclass
import os
import time
from typing import List

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.axes import Axes
from matplotlib import style

from threading import Thread

@dataclass
class LoggedProperty:
    name: str
    value: any = None
    live_logged: bool = True
    graph_id: int = None

class DataFrame:
    logged_properties = []
    def __init__(self, logged_properties: List[LoggedProperty]) -> None:
        self.logged_properties += logged_properties

    # allow df["x_target"] to be used as a shorthand for df.logged_properties["x_target"].value
    def __getitem__(self, key):
        for prop in self.logged_properties:
            if prop.name == key:
                return prop.value
        return None
    
    def __setitem__(self, key, value):
        for prop in self.logged_properties:
            if prop.name == key:
                prop.value = value
                return
        self.logged_properties.append(LoggedProperty(key, value))


class DataLogger:
    logged_properties = [
        LoggedProperty("step_start_time"),
        LoggedProperty("x_target", graph_id=0),
        LoggedProperty("x_current", graph_id=0),
        LoggedProperty("x_output", graph_id=0),
        LoggedProperty("x_error", graph_id=0),
        LoggedProperty("y_target", graph_id=1),
        LoggedProperty("y_current", graph_id=1),
        LoggedProperty("y_output", graph_id=1),
        LoggedProperty("y_error", graph_id=1),
        LoggedProperty("z_target", graph_id=2),
        LoggedProperty("z_current", graph_id=2),
        LoggedProperty("z_output", graph_id=2),
        LoggedProperty("z_error", graph_id=2),
        LoggedProperty("yaw_target", graph_id=3),
        LoggedProperty("yaw_current", graph_id=3),
        LoggedProperty("yaw_output", graph_id=3),
        LoggedProperty("yaw_error", graph_id=3),
    ]
    def __init__(self, filepath, logged_properties=None) -> None:
        self.filepath = filepath
        self.logged_properties = logged_properties if logged_properties is not None else DataLogger.logged_properties
        self.file_handle = open(self.filepath, "w")
        # this one is a  bit of a mess
        # it's writing the column names to the file
        # while also adding the graph_id to the name if it's not None, to tell the live grapher which graph to put it on
        self.file_handle.write(",".join([logged_prop.name if logged_prop.graph_id is None else f"{logged_prop.name}_{logged_prop.graph_id}" for logged_prop in self.logged_properties]) + "\n")
        self.file_handle.flush()
    
    def get_df(self):
        return DataFrame(self.logged_properties)
    
    def log(self, df: DataFrame):
        string_to_write = ""
        for logged_prop in df.logged_properties:
            # print(f"Logging {logged_prop.name} with value {logged_prop.value}")
            if logged_prop.value is None:
                print(f"WARN: {logged_prop.name} is None")
            string_to_write += str(logged_prop.value) + ","
        string_to_write = string_to_write[:-1] + "\n" # remove the trailing comma and add a newline
        # print(f"Writing to file: {string_to_write}")
        self.file_handle.write(string_to_write)
        self.file_handle.flush()

class LiveGrapher:
    def __init__(self, filepath, history_length_seconds):
        self.filepath = filepath
        self.history_length_seconds = history_length_seconds
        # data_to_plot will be a 3d array. each outer array is a plot, each inner array is a list of values for that plot. the first inner array is the x values.
        self.data_to_plot = [] 
        self.column_names = [] # a 2d array, same as above, but with the column names instead of the datasets, and  the first inner array is the title of the plot
        self.column_structure = [] # a 2d array, where each outer array is a plot and each inner array contains the column indices for that plot
    def live_graph(self):
        # do it!
        # kick off the data watcher, then set up the animation and hold onto it
        data_watcher = Thread(target=self.read_data)
        data_watcher.start()
        self.animate_plot()

    def parse_columns(self, column_string):
        column_names = column_string.split(",")
        # if a name ends in an underscore and a number, it's a graph id
        for column_index, column_name in enumerate(column_names):
            if column_name[-2] == "_":
                graph_id = int(column_name[-1])
                column_name = column_name[:-2]
                while len(self.data_to_plot) <= graph_id:
                    self.data_to_plot.append([[]])
                    self.column_names.append([])
                    self.column_structure.append([0]) # first column is x axis
                self.column_structure[graph_id].append(column_index)
                self.column_names[graph_id].append(column_name)
                self.data_to_plot[graph_id].append([])
            else:
                continue # ignore the column if it doesn't have a graph id
        # now go through the column names and try to get a graph name from the common prefix of each graph, and put that name in the first element of the column_names array
        for i in range(len(self.column_names)):
            common_prefix = os.path.commonprefix(self.column_names[i])
            self.column_names[i].insert(0, common_prefix[:-1]) # remove the trailing underscore
        print("Column parsing results:")
        print(self.column_names)
        print(self.column_structure)

    def read_data(self):
        # this watches the file and updates the data_to_plot array as needed. it runs in a separate thread.
        with open(self.filepath) as f:
            # read the first row to get the column names
            column_string = f.readline().strip()
            self.parse_columns(column_string)
            # follow as new lines are added to the file
            for line in self.follow(f):
                self.parse_line(line)
                self.trim_to_history_length()
    
    def parse_line(self, line):
        # parse the line
        values = line.strip().split(",")
        # add the values to the data_to_plot array
        for i in range(len(self.column_structure)):
            for j in range(len(self.column_structure[i])):
                #print(f"Adding {values[self.column_structure[i][j]]} to plot {i}, dataset {j}")
                #print(f"Data to plot: {self.data_to_plot[i]}")
                self.data_to_plot[i][j].append(float(values[self.column_structure[i][j]]))
    def trim_to_history_length(self):
        # trim the data_to_plot array to the last history_length_seconds of data
        for i in range(len(self.data_to_plot)):
            #print(f"Trimming plot {i} to times greater than {self.data_to_plot[i][0][len(self.data_to_plot[i][0])-1] - self.history_length_seconds}")
            while self.data_to_plot[i][0][0] < self.data_to_plot[i][0][len(self.data_to_plot[i][0])-1] - self.history_length_seconds:
                for j in range(len(self.data_to_plot[i])):
                    self.data_to_plot[i][j].pop(0)

    def follow(self, thefile):
        thefile.seek(0,2)
        while True:
            line = thefile.readline()
            if not line:
                time.sleep(0.02)
                continue
            yield line


    def render_plot(self, ax: Axes, axis_index, titles, error_history):
        history = self.data_to_plot[axis_index]
        # print(f"Rendering plot for {title} (history: {np.array2string(history, precision=2)}) (axis index {axis_index})")
        ax.clear()
        for i in range(1, len(history)):
            ax.plot(history[0], history[i], label=titles[i])
        ax.legend(loc='upper left')
        ax.set_title(titles[0])

    def animate_plot(self):
        style.use('fivethirtyeight')
        fig = plt.figure(dpi=150, figsize=(10, 6))
        axes = [fig.add_subplot(2, 2, i+1) for i in range(len(self.data_to_plot))]
        
        def animate(frame):
            for i in range(len(self.data_to_plot)):
                self.render_plot(axes[i], i, self.column_names[i], self.data_to_plot)
        ani = animation.FuncAnimation(fig, animate, interval=250, save_count=10) # hold on to this reference, or it will be garbage collected
        plt.show()

if __name__ == "__main__":
    LiveGrapher("live_data.csv", 10).live_graph()