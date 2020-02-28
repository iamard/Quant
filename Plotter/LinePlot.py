import os as os
import numpy as np
import pandas as pandas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm

class LinePlot:
    def __init__(self, plot_name, out_folder):
        self.plot_name  = plot_name
        self.out_folder = out_folder
        self.raw_data   = pandas.DataFrame()
    
    def add(self, record):
        self.raw_data = self.raw_data.append(record, ignore_index = True)

    def set(self, data):
        self.raw_data = data

    def data(self):
        return self.raw_data

    def plot(self, title, x_axis, color, style, marker):
        #pandas.plotting.register_matplotlib_converters()
        
        self.raw_data.sort_values(by = x_axis)
        self.raw_data.set_index(x_axis, inplace = True)

        plt.figure()
        fig, ax = plt.subplots()
        #plt.xticks(rotation = 45)
        
        color_it = iter(color)
        style_it = iter(style)
        marker_it = iter(marker)
        for col in self.raw_data.columns:
            self.raw_data[col].plot(
                x = self.raw_data.index,
                color = next(color_it), 
                linestyle = next(style_it), 
                marker = next(marker_it)
            )

        plt.title(title)
        plt.legend(self.raw_data.columns)

        fig.autofmt_xdate()
 
        file = os.path.join(self.out_folder, self.plot_name + '.png')
        plt.savefig(file, bbox_inches = "tight")
        plt.close()
