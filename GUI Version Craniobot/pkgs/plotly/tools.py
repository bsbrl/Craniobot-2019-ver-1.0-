# -*- coding: utf-8 -*-

"""
tools
=====

Functions that USERS will possibly want access to.

"""
from __future__ import absolute_import

import json
import warnings

import six
import re
import os

from plotly import exceptions, optional_imports
from plotly.files import PLOTLY_DIR

DEFAULT_PLOTLY_COLORS = ['rgb(31, 119, 180)', 'rgb(255, 127, 14)',
                         'rgb(44, 160, 44)', 'rgb(214, 39, 40)',
                         'rgb(148, 103, 189)', 'rgb(140, 86, 75)',
                         'rgb(227, 119, 194)', 'rgb(127, 127, 127)',
                         'rgb(188, 189, 34)', 'rgb(23, 190, 207)']


REQUIRED_GANTT_KEYS = ['Task', 'Start', 'Finish']
PLOTLY_SCALES = {'Greys': ['rgb(0,0,0)', 'rgb(255,255,255)'],
                 'YlGnBu': ['rgb(8,29,88)', 'rgb(255,255,217)'],
                 'Greens': ['rgb(0,68,27)', 'rgb(247,252,245)'],
                 'YlOrRd': ['rgb(128,0,38)', 'rgb(255,255,204)'],
                 'Bluered': ['rgb(0,0,255)', 'rgb(255,0,0)'],
                 'RdBu': ['rgb(5,10,172)', 'rgb(178,10,28)'],
                 'Reds': ['rgb(220,220,220)', 'rgb(178,10,28)'],
                 'Blues': ['rgb(5,10,172)', 'rgb(220,220,220)'],
                 'Picnic': ['rgb(0,0,255)', 'rgb(255,0,0)'],
                 'Rainbow': ['rgb(150,0,90)', 'rgb(255,0,0)'],
                 'Portland': ['rgb(12,51,131)', 'rgb(217,30,30)'],
                 'Jet': ['rgb(0,0,131)', 'rgb(128,0,0)'],
                 'Hot': ['rgb(0,0,0)', 'rgb(255,255,255)'],
                 'Blackbody': ['rgb(0,0,0)', 'rgb(160,200,255)'],
                 'Earth': ['rgb(0,0,130)', 'rgb(255,255,255)'],
                 'Electric': ['rgb(0,0,0)', 'rgb(255,250,220)'],
                 'Viridis': ['rgb(68,1,84)', 'rgb(253,231,37)']}

# color constants for violin plot
DEFAULT_FILLCOLOR = '#1f77b4'
DEFAULT_HISTNORM = 'probability density'
ALTERNATIVE_HISTNORM = 'probability'


# Warning format
def warning_on_one_line(message, category, filename, lineno,
                        file=None, line=None):
    return '%s:%s: %s:\n\n%s\n\n' % (filename, lineno, category.__name__,
                                     message)
warnings.formatwarning = warning_on_one_line

ipython_core_display = optional_imports.get_module('IPython.core.display')
sage_salvus = optional_imports.get_module('sage_salvus')


### mpl-related tools ###
def mpl_to_plotly(fig, resize=False, strip_style=False, verbose=False):
    """Convert a matplotlib figure to plotly dictionary and send.

    All available information about matplotlib visualizations are stored
    within a matplotlib.figure.Figure object. You can create a plot in python
    using matplotlib, store the figure object, and then pass this object to
    the fig_to_plotly function. In the background, mplexporter is used to
    crawl through the mpl figure object for appropriate information. This
    information is then systematically sent to the PlotlyRenderer which
    creates the JSON structure used to make plotly visualizations. Finally,
    these dictionaries are sent to plotly and your browser should open up a
    new tab for viewing! Optionally, if you're working in IPython, you can
    set notebook=True and the PlotlyRenderer will call plotly.iplot instead
    of plotly.plot to have the graph appear directly in the IPython notebook.

    Note, this function gives the user access to a simple, one-line way to
    render an mpl figure in plotly. If you need to trouble shoot, you can do
    this step manually by NOT running this fuction and entereing the following:

    ===========================================================================
    from plotly.matplotlylib import mplexporter, PlotlyRenderer

    # create an mpl figure and store it under a varialble 'fig'

    renderer = PlotlyRenderer()
    exporter = mplexporter.Exporter(renderer)
    exporter.run(fig)
    ===========================================================================

    You can then inspect the JSON structures by accessing these:

    renderer.layout -- a plotly layout dictionary
    renderer.data -- a list of plotly data dictionaries
    """
    matplotlylib = optional_imports.get_module('plotly.matplotlylib')
    if matplotlylib:
        renderer = matplotlylib.PlotlyRenderer()
        matplotlylib.Exporter(renderer).run(fig)
        if resize:
            renderer.resize()
        if strip_style:
            renderer.strip_style()
        if verbose:
            print(renderer.msg)
        return renderer.plotly_fig
    else:
        warnings.warn(
            "To use Plotly's matplotlylib functionality, you'll need to have "
            "matplotlib successfully installed with all of its dependencies. "
            "You're getting this error because matplotlib or one of its "
            "dependencies doesn't seem to be installed correctly.")


### graph_objs related tools ###

def get_subplots(rows=1, columns=1, print_grid=False, **kwargs):
    """Return a dictionary instance with the subplots set in 'layout'.

    Example 1:
    # stack two subplots vertically
    fig = tools.get_subplots(rows=2)
    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2], xaxis='x1', yaxis='y1')]
    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2], xaxis='x2', yaxis='y2')]

    Example 2:
    # print out string showing the subplot grid you've put in the layout
    fig = tools.get_subplots(rows=3, columns=2, print_grid=True)

    Keywords arguments with constant defaults:

    rows (kwarg, int greater than 0, default=1):
        Number of rows, evenly spaced vertically on the figure.

    columns (kwarg, int greater than 0, default=1):
        Number of columns, evenly spaced horizontally on the figure.

    horizontal_spacing (kwarg, float in [0,1], default=0.1):
        Space between subplot columns. Applied to all columns.

    vertical_spacing (kwarg, float in [0,1], default=0.05):
        Space between subplot rows. Applied to all rows.

    print_grid (kwarg, True | False, default=False):
        If True, prints a tab-delimited string representation
        of your plot grid.

    Keyword arguments with variable defaults:

    horizontal_spacing (kwarg, float in [0,1], default=0.2 / columns):
        Space between subplot columns.

    vertical_spacing (kwarg, float in [0,1], default=0.3 / rows):
        Space between subplot rows.

    """
    # TODO: protected until #282
    from plotly.graph_objs import graph_objs

    warnings.warn(
        "tools.get_subplots is depreciated. "
        "Please use tools.make_subplots instead."
    )

    # Throw exception for non-integer rows and columns
    if not isinstance(rows, int) or rows <= 0:
        raise Exception("Keyword argument 'rows' "
                        "must be an int greater than 0")
    if not isinstance(columns, int) or columns <= 0:
        raise Exception("Keyword argument 'columns' "
                        "must be an int greater than 0")

    # Throw exception if non-valid kwarg is sent
    VALID_KWARGS = ['horizontal_spacing', 'vertical_spacing']
    for key in kwargs.keys():
        if key not in VALID_KWARGS:
            raise Exception("Invalid keyword argument: '{0}'".format(key))

    # Set 'horizontal_spacing' / 'vertical_spacing' w.r.t. rows / columns
    try:
        horizontal_spacing = float(kwargs['horizontal_spacing'])
    except KeyError:
        horizontal_spacing = 0.2 / columns
    try:
        vertical_spacing = float(kwargs['vertical_spacing'])
    except KeyError:
        vertical_spacing = 0.3 / rows

    fig = dict(layout=graph_objs.Layout())  # will return this at the end
    plot_width = (1 - horizontal_spacing * (columns - 1)) / columns
    plot_height = (1 - vertical_spacing * (rows - 1)) / rows
    plot_num = 0
    for rrr in range(rows):
        for ccc in range(columns):
            xaxis_name = 'xaxis{0}'.format(plot_num + 1)
            x_anchor = 'y{0}'.format(plot_num + 1)
            x_start = (plot_width + horizontal_spacing) * ccc
            x_end = x_start + plot_width

            yaxis_name = 'yaxis{0}'.format(plot_num + 1)
            y_anchor = 'x{0}'.format(plot_num + 1)
            y_start = (plot_height + vertical_spacing) * rrr
            y_end = y_start + plot_height

            xaxis = dict(domain=[x_start, x_end], anchor=x_anchor)
            fig['layout'][xaxis_name] = xaxis
            yaxis = dict(domain=[y_start, y_end], anchor=y_anchor)
            fig['layout'][yaxis_name] = yaxis
            plot_num += 1

    if print_grid:
        print("This is the format of your plot grid!")
        grid_string = ""
        plot = 1
        for rrr in range(rows):
            grid_line = ""
            for ccc in range(columns):
                grid_line += "[{0}]\t".format(plot)
                plot += 1
            grid_string = grid_line + '\n' + grid_string
        print(grid_string)

    return graph_objs.Figure(fig)  # forces us to validate what we just did...


def make_subplots(rows=1, cols=1,
                  shared_xaxes=False, shared_yaxes=False,
                  start_cell='top-left', print_grid=True,
                  **kwargs):
    """Return an instance of plotly.graph_objs.Figure
    with the subplots domain set in 'layout'.

    Example 1:
    # stack two subplots vertically
    fig = tools.make_subplots(rows=2)

    This is the format of your plot grid:
    [ (1,1) x1,y1 ]
    [ (2,1) x2,y2 ]

    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2])]
    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2], xaxis='x2', yaxis='y2')]

    # or see Figure.append_trace

    Example 2:
    # subplots with shared x axes
    fig = tools.make_subplots(rows=2, shared_xaxes=True)

    This is the format of your plot grid:
    [ (1,1) x1,y1 ]
    [ (2,1) x1,y2 ]


    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2])]
    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2], yaxis='y2')]

    Example 3:
    # irregular subplot layout (more examples below under 'specs')
    fig = tools.make_subplots(rows=2, cols=2,
                              specs=[[{}, {}],
                                     [{'colspan': 2}, None]])

    This is the format of your plot grid!
    [ (1,1) x1,y1 ]  [ (1,2) x2,y2 ]
    [ (2,1) x3,y3           -      ]

    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2])]
    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2], xaxis='x2', yaxis='y2')]
    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2], xaxis='x3', yaxis='y3')]

    Example 4:
    # insets
    fig = tools.make_subplots(insets=[{'cell': (1,1), 'l': 0.7, 'b': 0.3}])

    This is the format of your plot grid!
    [ (1,1) x1,y1 ]

    With insets:
    [ x2,y2 ] over [ (1,1) x1,y1 ]

    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2])]
    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2], xaxis='x2', yaxis='y2')]

    Example 5:
    # include subplot titles
    fig = tools.make_subplots(rows=2, subplot_titles=('Plot 1','Plot 2'))

    This is the format of your plot grid:
    [ (1,1) x1,y1 ]
    [ (2,1) x2,y2 ]

    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2])]
    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2], xaxis='x2', yaxis='y2')]

    Example 6:
    # Include subplot title on one plot (but not all)
    fig = tools.make_subplots(insets=[{'cell': (1,1), 'l': 0.7, 'b': 0.3}],
                              subplot_titles=('','Inset'))

    This is the format of your plot grid!
    [ (1,1) x1,y1 ]

    With insets:
    [ x2,y2 ] over [ (1,1) x1,y1 ]

    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2])]
    fig['data'] += [Scatter(x=[1,2,3], y=[2,1,2], xaxis='x2', yaxis='y2')]

    Keywords arguments with constant defaults:

    rows (kwarg, int greater than 0, default=1):
        Number of rows in the subplot grid.

    cols (kwarg, int greater than 0, default=1):
        Number of columns in the subplot grid.

    shared_xaxes (kwarg, boolean or list, default=False)
        Assign shared x axes.
        If True, subplots in the same grid column have one common
        shared x-axis at the bottom of the gird.

        To assign shared x axes per subplot grid cell (see 'specs'),
        send list (or list of lists, one list per shared x axis)
        of cell index tuples.

    shared_yaxes (kwarg, boolean or list, default=False)
        Assign shared y axes.
        If True, subplots in the same grid row have one common
        shared y-axis on the left-hand side of the gird.

        To assign shared y axes per subplot grid cell (see 'specs'),
        send list (or list of lists, one list per shared y axis)
        of cell index tuples.

    start_cell (kwarg, 'bottom-left' or 'top-left', default='top-left')
        Choose the starting cell in the subplot grid used to set the
        domains of the subplots.

    print_grid (kwarg, boolean, default=True):
        If True, prints a tab-delimited string representation of
        your plot grid.

    Keyword arguments with variable defaults:

    horizontal_spacing (kwarg, float in [0,1], default=0.2 / cols):
        Space between subplot columns.
        Applies to all columns (use 'specs' subplot-dependents spacing)

    vertical_spacing (kwarg, float in [0,1], default=0.3 / rows):
        Space between subplot rows.
        Applies to all rows (use 'specs' subplot-dependents spacing)

    subplot_titles (kwarg, list of strings, default=empty list):
        Title of each subplot.
        "" can be included in the list if no subplot title is desired in
        that space so that the titles are properly indexed.

    specs (kwarg, list of lists of dictionaries):
        Subplot specifications.

        ex1: specs=[[{}, {}], [{'colspan': 2}, None]]

        ex2: specs=[[{'rowspan': 2}, {}], [None, {}]]

        - Indices of the outer list correspond to subplot grid rows
          starting from the bottom. The number of rows in 'specs'
          must be equal to 'rows'.

        - Indices of the inner lists correspond to subplot grid columns
          starting from the left. The number of columns in 'specs'
          must be equal to 'cols'.

        - Each item in the 'specs' list corresponds to one subplot
          in a subplot grid. (N.B. The subplot grid has exactly 'rows'
          times 'cols' cells.)

        - Use None for blank a subplot cell (or to move pass a col/row span).

        - Note that specs[0][0] has the specs of the 'start_cell' subplot.

        - Each item in 'specs' is a dictionary.
            The available keys are:

            * is_3d (boolean, default=False): flag for 3d scenes
            * colspan (int, default=1): number of subplot columns
                for this subplot to span.
            * rowspan (int, default=1): number of subplot rows
                for this subplot to span.
            * l (float, default=0.0): padding left of cell
            * r (float, default=0.0): padding right of cell
            * t (float, default=0.0): padding right of cell
            * b (float, default=0.0): padding bottom of cell

        - Use 'horizontal_spacing' and 'vertical_spacing' to adjust
          the spacing in between the subplots.

    insets (kwarg, list of dictionaries):
        Inset specifications.

        - Each item in 'insets' is a dictionary.
            The available keys are:

            * cell (tuple, default=(1,1)): (row, col) index of the
                subplot cell to overlay inset axes onto.
            * is_3d (boolean, default=False): flag for 3d scenes
            * l (float, default=0.0): padding left of inset
                  in fraction of cell width
            * w (float or 'to_end', default='to_end') inset width
                  in fraction of cell width ('to_end': to cell right edge)
            * b (float, default=0.0): padding bottom of inset
                  in fraction of cell height
            * h (float or 'to_end', default='to_end') inset height
                  in fraction of cell height ('to_end': to cell top edge)

    column_width (kwarg, list of numbers)
        Column_width specifications

        - Functions similarly to `column_width` of `plotly.graph_objs.Table`.
          Specify a list that contains numbers where the amount of numbers in
          the list is equal to `cols`.

        - The numbers in the list indicate the proportions that each column
          domains take across the full horizontal domain excluding padding.

        - For example, if columns_width=[3, 1], horizontal_spacing=0, and
          cols=2, the domains for each column would be [0. 0.75] and [0.75, 1]

    row_width (kwargs, list of numbers)
        Row_width specifications

        - Functions similarly to `column_width`. Specify a list that contains
          numbers where the amount of numbers in the list is equal to `rows`.

        - The numbers in the list indicate the proportions that each row
          domains take along the full vertical domain excluding padding.

        - For example, if row_width=[3, 1], vertical_spacing=0, and
          cols=2, the domains for each row from top to botton would be
          [0. 0.75] and [0.75, 1]
    """
    # TODO: protected until #282
    from plotly.graph_objs import graph_objs

    # Throw exception for non-integer rows and cols
    if not isinstance(rows, int) or rows <= 0:
        raise Exception("Keyword argument 'rows' "
                        "must be an int greater than 0")
    if not isinstance(cols, int) or cols <= 0:
        raise Exception("Keyword argument 'cols' "
                        "must be an int greater than 0")

    # Dictionary of things start_cell
    START_CELL_all = {
        'bottom-left': {
            # 'natural' setup where x & y domains increase monotonically
            'col_dir': 1,
            'row_dir': 1
        },
        'top-left': {
            # 'default' setup visually matching the 'specs' list of lists
            'col_dir': 1,
            'row_dir': -1
        }
        # TODO maybe add 'bottom-right' and 'top-right'
    }

    # Throw exception for invalid 'start_cell' values
    try:
        START_CELL = START_CELL_all[start_cell]
    except KeyError:
        raise Exception("Invalid 'start_cell' value")

    # Throw exception if non-valid kwarg is sent
    VALID_KWARGS = ['horizontal_spacing', 'vertical_spacing',
                    'specs', 'insets', 'subplot_titles', 'column_width',
                    'row_width']
    for key in kwargs.keys():
        if key not in VALID_KWARGS:
            raise Exception("Invalid keyword argument: '{0}'".format(key))

    # Set 'subplot_titles'
    subplot_titles = kwargs.get('subplot_titles', [""] * rows * cols)

    # Set 'horizontal_spacing' / 'vertical_spacing' w.r.t. rows / cols
    try:
        horizontal_spacing = float(kwargs['horizontal_spacing'])
    except KeyError:
        horizontal_spacing = 0.2 / cols
    try:
        vertical_spacing = float(kwargs['vertical_spacing'])
    except KeyError:
        if 'subplot_titles' in kwargs:
            vertical_spacing = 0.5 / rows
        else:
            vertical_spacing = 0.3 / rows

    # Sanitize 'specs' (must be a list of lists)
    exception_msg = "Keyword argument 'specs' must be a list of lists"
    try:
        specs = kwargs['specs']
        if not isinstance(specs, list):
            raise Exception(exception_msg)
        else:
            for spec_row in specs:
                if not isinstance(spec_row, list):
                    raise Exception(exception_msg)
    except KeyError:
        specs = [[{}
                 for c in range(cols)]
                 for r in range(rows)]     # default 'specs'

    # Throw exception if specs is over or under specified
    if len(specs) != rows:
        raise Exception("The number of rows in 'specs' "
                        "must be equal to 'rows'")
    for r, spec_row in enumerate(specs):
        if len(spec_row) != cols:
            raise Exception("The number of columns in 'specs' "
                            "must be equal to 'cols'")

    # Sanitize 'insets'
    try:
        insets = kwargs['insets']
        if not isinstance(insets, list):
            raise Exception("Keyword argument 'insets' must be a list")
    except KeyError:
        insets = False

    # Throw exception if non-valid key / fill in defaults
    def _check_keys_and_fill(name, arg, defaults):
        def _checks(item, defaults):
            if item is None:
                return
            if not isinstance(item, dict):
                raise Exception("Items in keyword argument '{name}' must be "
                                "dictionaries or None".format(name=name))
            for k in item.keys():
                if k not in defaults.keys():
                    raise Exception("Invalid key '{k}' in keyword "
                                    "argument '{name}'".format(k=k, name=name))
            for k in defaults.keys():
                if k not in item.keys():
                    item[k] = defaults[k]
        for arg_i in arg:
            if isinstance(arg_i, list):
                for arg_ii in arg_i:
                    _checks(arg_ii, defaults)
            elif isinstance(arg_i, dict):
                _checks(arg_i, defaults)

    # Default spec key-values
    SPEC_defaults = dict(
        is_3d=False,
        colspan=1,
        rowspan=1,
        l=0.0,
        r=0.0,
        b=0.0,
        t=0.0
        # TODO add support for 'w' and 'h'
    )
    _check_keys_and_fill('specs', specs, SPEC_defaults)

    # Default inset key-values
    if insets:
        INSET_defaults = dict(
            cell=(1, 1),
            is_3d=False,
            l=0.0,
            w='to_end',
            b=0.0,
            h='to_end'
        )
        _check_keys_and_fill('insets', insets, INSET_defaults)

    # set heights (with 'column_width')
    try:
        column_width = kwargs['column_width']
        if not isinstance(column_width, list) or len(column_width) != cols:
            raise Exception(
                "Keyword argument 'column_width' must be a list with {} "
                "numbers in it, the number of subplot cols.".format(cols)
            )
    except KeyError:
        column_width = None

    if column_width:
        cum_sum = float(sum(column_width))
        widths = []
        for w in column_width:
            widths.append(
                (1. - horizontal_spacing * (cols - 1)) * (w / cum_sum)
            )
    else:
        widths = [(1. - horizontal_spacing * (cols - 1)) / cols] * cols

    # set widths (with 'row_width')
    try:
        row_width = kwargs['row_width']
        if not isinstance(row_width, list) or len(row_width) != rows:
            raise Exception(
                "Keyword argument 'row_width' must be a list with {} "
                "numbers in it, the number of subplot rows.".format(rows)
            )
    except KeyError:
        row_width = None

    if row_width:
        cum_sum = float(sum(row_width))
        heights = []
        for h in row_width:
            heights.append(
                (1. - vertical_spacing * (rows - 1)) * (h / cum_sum)
            )
    else:
        heights = [(1. - vertical_spacing * (rows - 1)) / rows] * rows

    # Built row/col sequence using 'row_dir' and 'col_dir'
    COL_DIR = START_CELL['col_dir']
    ROW_DIR = START_CELL['row_dir']
    col_seq = range(cols)[::COL_DIR]
    row_seq = range(rows)[::ROW_DIR]

    # [grid] Build subplot grid (coord tuple of cell)
    grid = [
        [
            (
                (sum(widths[:c]) + c * horizontal_spacing),
                (sum(heights[:r]) + r * vertical_spacing)
            ) for c in col_seq
        ] for r in row_seq
    ]
    # [grid_ref] Initialize the grid and insets' axis-reference lists
    grid_ref = [[None for c in range(cols)] for r in range(rows)]
    insets_ref = [None for inset in range(len(insets))] if insets else None

    layout = graph_objs.Layout()  # init layout object

    # Function handling logic around 2d axis labels
    # Returns 'x{}' | 'y{}'
    def _get_label(x_or_y, r, c, cnt, shared_axes):
        # Default label (given strictly by cnt)
        label = "{x_or_y}{cnt}".format(x_or_y=x_or_y, cnt=cnt)

        if isinstance(shared_axes, bool):
            if shared_axes:
                if x_or_y == 'x':
                    label = "{x_or_y}{c}".format(x_or_y=x_or_y, c=c + 1)
                if x_or_y == 'y':
                    label = "{x_or_y}{r}".format(x_or_y=x_or_y, r=r + 1)

        if isinstance(shared_axes, list):
            if isinstance(shared_axes[0], tuple):
                shared_axes = [shared_axes]  # TODO put this elsewhere
            for shared_axis in shared_axes:
                if (r + 1, c + 1) in shared_axis:
                    label = {
                        'x': "x{0}".format(shared_axis[0][1]),
                        'y': "y{0}".format(shared_axis[0][0])
                    }[x_or_y]

        return label

    # Row in grid of anchor row if shared_xaxes=True
    ANCHOR_ROW = 0 if ROW_DIR > 0 else rows - 1

    # Function handling logic around 2d axis anchors
    # Return 'x{}' | 'y{}' | 'free' | False
    def _get_anchors(r, c, x_cnt, y_cnt, shared_xaxes, shared_yaxes):
        # Default anchors (give strictly by cnt)
        x_anchor = "y{y_cnt}".format(y_cnt=y_cnt)
        y_anchor = "x{x_cnt}".format(x_cnt=x_cnt)

        if isinstance(shared_xaxes, bool):
            if shared_xaxes:
                if r != ANCHOR_ROW:
                    x_anchor = False
                    y_anchor = 'free'
                    if shared_yaxes and c != 0:  # TODO covers all cases?
                        y_anchor = False
                    return x_anchor, y_anchor

        elif isinstance(shared_xaxes, list):
            if isinstance(shared_xaxes[0], tuple):
                shared_xaxes = [shared_xaxes]  # TODO put this elsewhere
            for shared_xaxis in shared_xaxes:
                if (r + 1, c + 1) in shared_xaxis[1:]:
                    x_anchor = False
                    y_anchor = 'free'  # TODO covers all cases?

        if isinstance(shared_yaxes, bool):
            if shared_yaxes:
                if c != 0:
                    y_anchor = False
                    x_anchor = 'free'
                    if shared_xaxes and r != ANCHOR_ROW:  # TODO all cases?
                        x_anchor = False
                    return x_anchor, y_anchor

        elif isinstance(shared_yaxes, list):
            if isinstance(shared_yaxes[0], tuple):
                shared_yaxes = [shared_yaxes]  # TODO put this elsewhere
            for shared_yaxis in shared_yaxes:
                if (r + 1, c + 1) in shared_yaxis[1:]:
                    y_anchor = False
                    x_anchor = 'free'  # TODO covers all cases?

        return x_anchor, y_anchor

    list_of_domains = []  # added for subplot titles

    # Function pasting x/y domains in layout object (2d case)
    def _add_domain(layout, x_or_y, label, domain, anchor, position):
        name = label[0] + 'axis' + label[1:]

        # Clamp domain elements between [0, 1].
        # This is only needed to combat numerical precision errors
        # See GH1031
        axis = {'domain': [max(0.0, domain[0]), min(1.0, domain[1])]}
        if anchor:
            axis['anchor'] = anchor
        if isinstance(position, float):
            axis['position'] = position
        layout[name] = axis
        list_of_domains.append(domain)  # added for subplot titles

    # Function pasting x/y domains in layout object (3d case)
    def _add_domain_is_3d(layout, s_label, x_domain, y_domain):
        scene = dict(
            domain={'x': [max(0.0, x_domain[0]), min(1.0, x_domain[1])],
                    'y': [max(0.0, y_domain[0]), min(1.0, y_domain[1])]})
        layout[s_label] = scene

    x_cnt = y_cnt = s_cnt = 1  # subplot axis/scene counters

    # Loop through specs -- (r, c) <-> (row, col)
    for r, spec_row in enumerate(specs):
        for c, spec in enumerate(spec_row):

            if spec is None:  # skip over None cells
                continue

            c_spanned = c + spec['colspan'] - 1  # get spanned c
            r_spanned = r + spec['rowspan'] - 1  # get spanned r

            # Throw exception if 'colspan' | 'rowspan' is too large for grid
            if c_spanned >= cols:
                raise Exception("Some 'colspan' value is too large for "
                                "this subplot grid.")
            if r_spanned >= rows:
                raise Exception("Some 'rowspan' value is too large for "
                                "this subplot grid.")

            # Get x domain using grid and colspan
            x_s = grid[r][c][0] + spec['l']
            x_e = grid[r][c_spanned][0] + widths[c] - spec['r']
            x_domain = [x_s, x_e]

            # Get y domain (dep. on row_dir) using grid & r_spanned
            if ROW_DIR > 0:
                y_s = grid[r][c][1] + spec['b']
                y_e = grid[r_spanned][c][1] + heights[-1 - r] - spec['t']
            else:
                y_s = grid[r_spanned][c][1] + spec['b']
                y_e = grid[r][c][1] + heights[-1 - r] - spec['t']
            y_domain = [y_s, y_e]

            if spec['is_3d']:

                # Add scene to layout
                s_label = 'scene{0}'.format(s_cnt)
                _add_domain_is_3d(layout, s_label, x_domain, y_domain)
                grid_ref[r][c] = (s_label, )
                s_cnt += 1

            else:

                # Get axis label and anchor
                x_label = _get_label('x', r, c, x_cnt, shared_xaxes)
                y_label = _get_label('y', r, c, y_cnt, shared_yaxes)
                x_anchor, y_anchor = _get_anchors(r, c,
                                                  x_cnt, y_cnt,
                                                  shared_xaxes,
                                                  shared_yaxes)

                # Add a xaxis to layout (N.B anchor == False -> no axis)
                if x_anchor:
                    if x_anchor == 'free':
                        x_position = y_domain[0]
                    else:
                        x_position = False
                    _add_domain(layout, 'x', x_label, x_domain,
                                x_anchor, x_position)
                    x_cnt += 1

                # Add a yaxis to layout (N.B anchor == False -> no axis)
                if y_anchor:
                    if y_anchor == 'free':
                        y_position = x_domain[0]
                    else:
                        y_position = False
                    _add_domain(layout, 'y', y_label, y_domain,
                                y_anchor, y_position)
                    y_cnt += 1

                grid_ref[r][c] = (x_label, y_label)  # fill in ref

    # Loop through insets
    if insets:
        for i_inset, inset in enumerate(insets):

            r = inset['cell'][0] - 1
            c = inset['cell'][1] - 1

            # Throw exception if r | c is out of range
            if not (0 <= r < rows):
                raise Exception("Some 'cell' row value is out of range. "
                                "Note: the starting cell is (1, 1)")
            if not (0 <= c < cols):
                raise Exception("Some 'cell' col value is out of range. "
                                "Note: the starting cell is (1, 1)")

            # Get inset x domain using grid
            x_s = grid[r][c][0] + inset['l'] * widths[c]
            if inset['w'] == 'to_end':
                x_e = grid[r][c][0] + widths[c]
            else:
                x_e = x_s + inset['w'] * widths[c]
            x_domain = [x_s, x_e]

            # Get inset y domain using grid
            y_s = grid[r][c][1] + inset['b'] * heights[-1 - r]
            if inset['h'] == 'to_end':
                y_e = grid[r][c][1] + heights[-1 - r]
            else:
                y_e = y_s + inset['h'] * heights[-1 - r]
            y_domain = [y_s, y_e]

            if inset['is_3d']:

                # Add scene to layout
                s_label = 'scene{0}'.format(s_cnt)
                _add_domain_is_3d(layout, s_label, x_domain, y_domain)
                insets_ref[i_inset] = (s_label, )
                s_cnt += 1

            else:

                # Get axis label and anchor
                x_label = _get_label('x', False, False, x_cnt, False)
                y_label = _get_label('y', False, False, y_cnt, False)
                x_anchor, y_anchor = _get_anchors(r, c,
                                                  x_cnt, y_cnt,
                                                  False, False)

                # Add a xaxis to layout (N.B insets always have anchors)
                _add_domain(layout, 'x', x_label, x_domain, x_anchor, False)
                x_cnt += 1

                # Add a yayis to layout (N.B insets always have anchors)
                _add_domain(layout, 'y', y_label, y_domain, y_anchor, False)
                y_cnt += 1

                insets_ref[i_inset] = (x_label, y_label)  # fill in ref

    # [grid_str] Set the grid's string representation
    sp = "  "            # space between cell
    s_str = "[ "         # cell start string
    e_str = " ]"         # cell end string
    colspan_str = '       -'     # colspan string
    rowspan_str = '       |'     # rowspan string
    empty_str = '    (empty) '   # empty cell string

    # Init grid_str with intro message
    grid_str = "This is the format of your plot grid:\n"

    # Init tmp list of lists of strings (sorta like 'grid_ref' but w/ strings)
    _tmp = [['' for c in range(cols)] for r in range(rows)]

    # Define cell string as function of (r, c) and grid_ref
    def _get_cell_str(r, c, ref):
        return '({r},{c}) {ref}'.format(r=r + 1, c=c + 1, ref=','.join(ref))

    # Find max len of _cell_str, add define a padding function
    cell_len = max([len(_get_cell_str(r, c, ref))
                    for r, row_ref in enumerate(grid_ref)
                    for c, ref in enumerate(row_ref)
                    if ref]) + len(s_str) + len(e_str)

    def _pad(s, cell_len=cell_len):
        return ' ' * (cell_len - len(s))

    # Loop through specs, fill in _tmp
    for r, spec_row in enumerate(specs):
        for c, spec in enumerate(spec_row):

            ref = grid_ref[r][c]
            if ref is None:
                if _tmp[r][c] == '':
                    _tmp[r][c] = empty_str + _pad(empty_str)
                continue

            cell_str = s_str + _get_cell_str(r, c, ref)

            if spec['colspan'] > 1:
                for cc in range(1, spec['colspan'] - 1):
                    _tmp[r][c + cc] = colspan_str + _pad(colspan_str)
                _tmp[r][c + spec['colspan'] - 1] = (
                    colspan_str + _pad(colspan_str + e_str)) + e_str
            else:
                cell_str += e_str

            if spec['rowspan'] > 1:
                for rr in range(1, spec['rowspan'] - 1):
                    _tmp[r + rr][c] = rowspan_str + _pad(rowspan_str)
                for cc in range(spec['colspan']):
                    _tmp[r + spec['rowspan'] - 1][c + cc] = (
                        rowspan_str + _pad(rowspan_str))

            _tmp[r][c] = cell_str + _pad(cell_str)

    # Append grid_str using data from _tmp in the correct order
    for r in row_seq[::-1]:
        grid_str += sp.join(_tmp[r]) + '\n'

    # Append grid_str to include insets info
    if insets:
        grid_str += "\nWith insets:\n"
        for i_inset, inset in enumerate(insets):

            r = inset['cell'][0] - 1
            c = inset['cell'][1] - 1
            ref = grid_ref[r][c]

            grid_str += (
                s_str + ','.join(insets_ref[i_inset]) + e_str +
                ' over ' +
                s_str + _get_cell_str(r, c, ref) + e_str + '\n'
            )

    # Add subplot titles

    # If shared_axes is False (default) use list_of_domains
    # This is used for insets and irregular layouts
    if not shared_xaxes and not shared_yaxes:
        x_dom = list_of_domains[::2]
        y_dom = list_of_domains[1::2]
        subtitle_pos_x = []
        subtitle_pos_y = []
        for x_domains in x_dom:
            subtitle_pos_x.append(sum(x_domains) / 2)
        for y_domains in y_dom:
            subtitle_pos_y.append(y_domains[1])

    # If shared_axes is True the domin of each subplot is not returned so the
    # title position must be calculated for each subplot
    else:
        x_dom_vals = [k for k in layout.to_plotly_json().keys() if 'xaxis' in k]
        y_dom_vals = [k for k in layout.to_plotly_json().keys() if 'yaxis' in k]

        # sort xaxis and yaxis layout keys
        r = re.compile('\d+')

        def key_func(m):
            try:
                return int(r.search(m).group(0))
            except AttributeError:
                return 0

        xaxies_labels_sorted = sorted(x_dom_vals, key=key_func)
        yaxies_labels_sorted = sorted(y_dom_vals, key=key_func)

        x_dom = [layout[k]['domain'] for k in xaxies_labels_sorted]
        y_dom = [layout[k]['domain'] for k in yaxies_labels_sorted]

        for index in range(cols):
            subtitle_pos_x = []
            for x_domains in x_dom:
                subtitle_pos_x.append(sum(x_domains) / 2)
            subtitle_pos_x *= rows

        if shared_yaxes:
            for index in range(rows):
                subtitle_pos_y = []
                for y_domain in y_dom:
                    subtitle_pos_y.append(y_domain[1])
                subtitle_pos_y *= cols
            subtitle_pos_y = sorted(subtitle_pos_y, reverse=True)

        else:
            for index in range(rows):
                subtitle_pos_y = []
                for y_domain in y_dom:
                    subtitle_pos_y.append(y_domain[1])
            subtitle_pos_y = sorted(subtitle_pos_y, reverse=True)
            subtitle_pos_y *= cols

    plot_titles = []
    for index in range(len(subplot_titles)):
        if not subplot_titles[index]:
            pass
        else:
            plot_titles.append({'y': subtitle_pos_y[index],
                                'xref': 'paper',
                                'x': subtitle_pos_x[index],
                                'yref': 'paper',
                                'text': subplot_titles[index],
                                'showarrow': False,
                                'font': dict(size=16),
                                'xanchor': 'center',
                                'yanchor': 'bottom'
                                })

            layout['annotations'] = plot_titles

    if print_grid:
        print(grid_str)

    fig = graph_objs.Figure(layout=layout)

    fig.__dict__['_grid_ref'] = grid_ref
    fig.__dict__['_grid_str'] = grid_str

    return fig


def get_graph_obj(obj, obj_type=None):
    """Returns a new graph object.

    OLD FUNCTION: this will *silently* strip out invalid pieces of the object.
    NEW FUNCTION: no striping of invalid pieces anymore - only raises error
        on unrecognized graph_objs
    """
    # TODO: Deprecate or move. #283
    from plotly.graph_objs import graph_objs
    try:
        cls = getattr(graph_objs, obj_type)
    except (AttributeError, KeyError):
        raise exceptions.PlotlyError(
            "'{}' is not a recognized graph_obj.".format(obj_type)
        )
    return cls(obj)


def validate(obj, obj_type):
    """Validate a dictionary, list, or graph object as 'obj_type'.

    This will not alter the 'obj' referenced in the call signature. It will
    raise an error if the 'obj' reference could not be instantiated as a
    valid 'obj_type' graph object.

    """
    # TODO: Deprecate or move. #283
    from plotly import graph_reference
    from plotly.graph_objs import graph_objs

    if obj_type not in graph_reference.CLASSES:
        obj_type = graph_reference.string_to_class_name(obj_type)

    try:
        cls = getattr(graph_objs, obj_type)
    #except AttributeError:
    except ValueError:
        raise exceptions.PlotlyError(
            "'{0}' is not a recognizable graph_obj.".
            format(obj_type))
    cls(obj)  # this will raise on invalid keys/items


def _replace_newline(obj):
    """Replaces '\n' with '<br>' for all strings in a collection."""
    if isinstance(obj, dict):
        d = dict()
        for key, val in list(obj.items()):
            d[key] = _replace_newline(val)
        return d
    elif isinstance(obj, list):
        l = list()
        for index, entry in enumerate(obj):
            l += [_replace_newline(entry)]
        return l
    elif isinstance(obj, six.string_types):
        s = obj.replace('\n', '<br>')
        if s != obj:
            warnings.warn("Looks like you used a newline character: '\\n'.\n\n"
                          "Plotly uses a subset of HTML escape characters\n"
                          "to do things like newline (<br>), bold (<b></b>),\n"
                          "italics (<i></i>), etc. Your newline characters \n"
                          "have been converted to '<br>' so they will show \n"
                          "up right on your Plotly figure!")
        return s
    else:
        return obj  # we return the actual reference... but DON'T mutate.


def return_figure_from_figure_or_data(figure_or_data, validate_figure):
    from plotly.graph_objs import Figure
    from plotly.basedatatypes import BaseFigure

    validated = False
    if isinstance(figure_or_data, dict):
        figure = figure_or_data
    elif isinstance(figure_or_data, list):
        figure = {'data': figure_or_data}
    elif isinstance(figure_or_data, BaseFigure):
        figure = figure_or_data.to_dict()
        validated = True
    else:
        raise exceptions.PlotlyError("The `figure_or_data` positional "
                                     "argument must be "
                                     "`dict`-like, `list`-like, or an instance of plotly.graph_objs.Figure")

    if validate_figure and not validated:

        try:
            figure = Figure(**figure).to_dict()
        except exceptions.PlotlyError as err:
            raise exceptions.PlotlyError("Invalid 'figure_or_data' argument. "
                                         "Plotly will not be able to properly "
                                         "parse the resulting JSON. If you "
                                         "want to send this 'figure_or_data' "
                                         "to Plotly anyway (not recommended), "
                                         "you can set 'validate=False' as a "
                                         "plot option.\nHere's why you're "
                                         "seeing this error:\n\n{0}"
                                         "".format(err))
        if not figure['data']:
            raise exceptions.PlotlyEmptyDataError(
                "Empty data list found. Make sure that you populated the "
                "list of data objects you're sending and try again.\n"
                "Questions? Visit support.plot.ly"
            )

    return figure

# Default colours for finance charts
_DEFAULT_INCREASING_COLOR = '#3D9970'  # http://clrs.cc
_DEFAULT_DECREASING_COLOR = '#FF4136'

DIAG_CHOICES = ['scatter', 'histogram', 'box']
VALID_COLORMAP_TYPES = ['cat', 'seq']

# Deprecations
class FigureFactory(object):

    @staticmethod
    def _deprecated(old_method, new_method=None):
        if new_method is None:
            # The method name stayed the same.
            new_method = old_method
        warnings.warn(
            'plotly.tools.FigureFactory.{} is deprecated. '
            'Use plotly.figure_factory.{}'.format(old_method, new_method)
        )

    @staticmethod
    def create_2D_density(*args, **kwargs):
        FigureFactory._deprecated('create_2D_density', 'create_2d_density')
        from plotly.figure_factory import create_2d_density
        return create_2d_density(*args, **kwargs)

    @staticmethod
    def create_annotated_heatmap(*args, **kwargs):
        FigureFactory._deprecated('create_annotated_heatmap')
        from plotly.figure_factory import create_annotated_heatmap
        return create_annotated_heatmap(*args, **kwargs)

    @staticmethod
    def create_candlestick(*args, **kwargs):
        FigureFactory._deprecated('create_candlestick')
        from plotly.figure_factory import create_candlestick
        return create_candlestick(*args, **kwargs)

    @staticmethod
    def create_dendrogram(*args, **kwargs):
        FigureFactory._deprecated('create_dendrogram')
        from plotly.figure_factory import create_dendrogram
        return create_dendrogram(*args, **kwargs)

    @staticmethod
    def create_distplot(*args, **kwargs):
        FigureFactory._deprecated('create_distplot')
        from plotly.figure_factory import create_distplot
        return create_distplot(*args, **kwargs)

    @staticmethod
    def create_facet_grid(*args, **kwargs):
        FigureFactory._deprecated('create_facet_grid')
        from plotly.figure_factory import create_facet_grid
        return create_facet_grid(*args, **kwargs)

    @staticmethod
    def create_gantt(*args, **kwargs):
        FigureFactory._deprecated('create_gantt')
        from plotly.figure_factory import create_gantt
        return create_gantt(*args, **kwargs)

    @staticmethod
    def create_ohlc(*args, **kwargs):
        FigureFactory._deprecated('create_ohlc')
        from plotly.figure_factory import create_ohlc
        return create_ohlc(*args, **kwargs)

    @staticmethod
    def create_quiver(*args, **kwargs):
        FigureFactory._deprecated('create_quiver')
        from plotly.figure_factory import create_quiver
        return create_quiver(*args, **kwargs)

    @staticmethod
    def create_scatterplotmatrix(*args, **kwargs):
        FigureFactory._deprecated('create_scatterplotmatrix')
        from plotly.figure_factory import create_scatterplotmatrix
        return create_scatterplotmatrix(*args, **kwargs)

    @staticmethod
    def create_streamline(*args, **kwargs):
        FigureFactory._deprecated('create_streamline')
        from plotly.figure_factory import create_streamline
        return create_streamline(*args, **kwargs)

    @staticmethod
    def create_table(*args, **kwargs):
        FigureFactory._deprecated('create_table')
        from plotly.figure_factory import create_table
        return create_table(*args, **kwargs)

    @staticmethod
    def create_trisurf(*args, **kwargs):
        FigureFactory._deprecated('create_trisurf')
        from plotly.figure_factory import create_trisurf
        return create_trisurf(*args, **kwargs)

    @staticmethod
    def create_violin(*args, **kwargs):
        FigureFactory._deprecated('create_violin')
        from plotly.figure_factory import create_violin
        return create_violin(*args, **kwargs)


def get_config_plotly_server_url():
    """
    Function to get the .config file's 'plotly_domain' without importing
    the chart_studio package.  This property is needed to compute the default
    value of the plotly.js config plotlyServerURL, so it is independent of
    the chart_studio integration and still needs to live in

    Returns
    -------
    str
    """
    config_file = os.path.join(PLOTLY_DIR, ".config")
    default_server_url = 'https://plot.ly'
    if not os.path.exists(config_file):
        return default_server_url
    with open(config_file, 'rt') as f:
        try:
            config_dict = json.load(f)
            if not isinstance(config_dict, dict):
                data = {}
        except:
            # TODO: issue a warning and bubble it up
            data = {}

    return config_dict.get('plotly_domain', default_server_url)


# get_config_defaults
from _plotly_future_ import _future_flags

if 'remove_deprecations' not in _future_flags:
    from _plotly_future_ import _chart_studio_deprecation

    from chart_studio.tools import (get_config_defaults)
    get_config_defaults = _chart_studio_deprecation(
        get_config_defaults)

    # ensure_local_plotly_files
    from chart_studio.tools import ensure_local_plotly_files
    ensure_local_plotly_files = _chart_studio_deprecation(
        ensure_local_plotly_files)

    # set_credentials_file
    from chart_studio.tools import set_credentials_file
    set_credentials_file = _chart_studio_deprecation(
        set_credentials_file)

    # get_credentials_file
    from chart_studio.tools import get_credentials_file
    get_credentials_file = _chart_studio_deprecation(
        get_credentials_file)

    # reset_credentials_file
    from chart_studio.tools import reset_credentials_file
    reset_credentials_file = _chart_studio_deprecation(
        reset_credentials_file)

    # set_config_file
    from chart_studio.tools import set_config_file
    set_config_file = _chart_studio_deprecation(
        set_config_file)

    # get_config_file
    from chart_studio.tools import get_config_file
    get_config_file = _chart_studio_deprecation(
        get_config_file)

    # reset_config_file
    from chart_studio.tools import reset_config_file
    reset_config_file = _chart_studio_deprecation(
        reset_config_file)

    # get_embed
    from chart_studio.tools import get_embed
    get_embed = _chart_studio_deprecation(
        get_embed)

    # embed
    from chart_studio.tools import embed
    embed = _chart_studio_deprecation(
        embed)
