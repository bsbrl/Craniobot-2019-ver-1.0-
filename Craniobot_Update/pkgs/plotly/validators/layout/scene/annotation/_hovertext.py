import _plotly_utils.basevalidators


class HovertextValidator(_plotly_utils.basevalidators.StringValidator):

    def __init__(
        self,
        plotly_name='hovertext',
        parent_name='layout.scene.annotation',
        **kwargs
    ):
        super(HovertextValidator, self).__init__(
            plotly_name=plotly_name,
            parent_name=parent_name,
            edit_type=kwargs.pop('edit_type', 'calc'),
            role=kwargs.pop('role', 'info'),
            **kwargs
        )
