import pandas as pd
import numpy as np
import pandas_bokeh
from math import pi
#pd.set_option('plotting.backend', 'pandas_bokeh')

from bokeh.models import LinearColorMapper, ColorBar, FixedTicker
from bokeh.palettes import brewer, Viridis5, Category10
from bokeh.plotting import figure, show, output_file
from bokeh.models import Slider, HoverTool, Select, CustomJS, ColumnDataSource, FactorRange, NumeralTickFormatter, LabelSet
from bokeh.layouts import widgetbox, row, column
from bokeh.transform import cumsum

df = pd.read_csv('../data/antibiotic_exposed_vs_no_antibiotic_proportion.csv', delimiter=',')
print(df.shape)

"""
pie_chart = df.plot_bokeh.pie(
    x="type",
    y="1001_Medical Wardpercentage",
    colormap = ["green", "yellow", "red"],
    title="Ratio of antibiotic and no-antibiotic",
    show_figure=False,
    return_html=True,
    line_color="grey")
"""

#data = pd.Series(x).reset_index(name='value').rename(columns={'index':'country'})
df['percentage'] = df['1001_24-Hour Observation Areapercentage']
df['angle'] = df['1001_24-Hour Observation Areapercentage'] * 2 * pi
df['color'] = Category10[len(df)]

print(df.head(10))

pie_chart = figure(plot_height=350, title="Pie Chart", toolbar_location=None,
        tools="hover", tooltips="@type: @percentage%")

pie_chart.wedge(x=1, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend='type', source=df)
source = ColumnDataSource(df)
source.data['formatted_percentage'] = ["    %.2f" % x for x in source.data['percentage']]
#labels = LabelSet(x=1, y=1, text='formatted_percentage',
#        angle=cumsum('angle', include_zero=True), source=source, render_mode='canvas')

#pie_chart.add_layout(labels)
#pie_chart.legend.location = "center"
#pie_chart.add_layout(pie_chart.legend[0], 'right')

#show(pie_chart)


# prepare some data
x = [1, 2, 3, 4, 5]
y = [6, 7, 2, 4, 5]
# create a new plot with a title and axis labels
p = figure(title="Simple line example", x_axis_label='x', y_axis_label='y')
# add a line renderer with legend and line thickness to the plot
p.line(x, y, legend_label="Temp.", line_width=2)
#show(p)

layout = row(pie_chart, p)
show(layout)
