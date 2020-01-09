import os as os
import pandas as pandas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class LinePlot:
    def __init__(self, plot_name, out_folder):
        self.plot_name  = plot_name
        self.out_folder = out_folder
        self.raw_data   = pandas.DataFrame()
    
    def add(self, record):
        self.raw_data = self.raw_data.append(record, ignore_index = True)

    def plot(self, x_axis, color, style, marker):
        #pandas.plotting.register_matplotlib_converters()
        
        self.raw_data.sort_values(by = x_axis)
        self.raw_data.set_index(x_axis, inplace = True)

        plt.figure()
        plt.xticks(rotation = 45)

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

        plt.title(self.plot_name)
        plt.legend(self.raw_data.columns)
        
        file = os.path.join(self.out_folder, self.plot_name + '.png')
        plt.savefig(file, bbox_inches = "tight")
        plt.close()