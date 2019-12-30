import _plotly_utils.basevalidators


class RangemodeValidator(_plotly_utils.basevalidators.EnumeratedValidator):

    def __init__(
        self,
        plotly_name='rangemode',
        parent_name='layout.scene.yaxis',
        **kwargs
    ):
        super(RangemodeValidator, self).__init__(
            plotly_name=plotly_name,
            parent_name=parent_name,
            edit_type=kwargs.pop('edit_type', 'plot'),
            role=kwargs.pop('role', 'info'),
            values=kwargs.pop('values', ['normal', 'tozero', 'nonnegative']),
            **kwargs
        )
