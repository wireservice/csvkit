"""
This module contains all style configuration for rendering charts. Setting any
of these variables will change how charts are rendered.
"""

# CHART

#: Default chart width
default_chart_width = 800

#: Default chart height
default_chart_height = 600

#: Chart background color
background_color = '#f9f9f9'

#: Chart margin as a percent of chart width
margin = 0.05

# CHART TITLE

#: Chart title text color
title_color = '#333'

#: Chart title font
title_font_family = 'Monaco'

#: Chart title font size
title_font_size = 16

#: Approximate glyph height of the title font
title_font_char_height = 16

#: Approximate glyph width of the title font
title_font_char_width = 9

#: Gap between title and rest of chart
title_gap = 4

# LEGEND

#: Chart legend text color
legend_color = '#666'

#: Chart legend font
legend_font_family = 'Monaco'

#: Chart legend font size
legend_font_size = 14

#: Approximate glyph height of the legend font
legend_font_char_height = 14

#: Approximate glyph width of the legend font
legend_font_char_width = 8

#: Gap between legend and rest of chart
legend_gap = 4

#: Size of the bubble next to an legend item
legend_bubble_size = 10

#: Offset from the top of the glyph
legend_bubble_offset = 4

# AXIS

#: Axis title text color
axis_title_color = '#666'

#: Axis title font
axis_title_font_family = 'Monaco'

#: Axis title font size
axis_title_font_size = 14

#: Approximate glyph height of the axis title font
axis_title_font_char_height = 14

#: Approximate glyph width of the axis title font
axis_title_font_char_width = 8

#: Gap between axis title and rest of chart
axis_title_gap = 16

# TICKS

#: Width of a tick mark
tick_width = 1

#: Length of a tick mark
tick_size = 4

#: Color of tick marks
tick_color = '#eee'

#: Color of the zero tick mark
zero_color = '#a8a8a8'

# TICK LABELS

#: Color of tick label text
label_color = '#9c9c9c'

#: Tick label font
tick_font_family = 'Monaco'

#: Tick label font size
tick_font_size = 14

#: Approximate glyph height of the tick label font
tick_font_char_height = 14

#: Approximate glyph width of the tick label font
tick_font_char_width = 8

# SERIES

#: Default sequence of :class:`.Shape` colors
default_series_colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']

#: Default :class:`.Dots` radius
default_dot_radius = 3

#: Default :class:`.Line` width
default_line_width = 2

#: Default stroke-dasharray property when using dashes on a line
default_stroke_dasharray = 'none'
