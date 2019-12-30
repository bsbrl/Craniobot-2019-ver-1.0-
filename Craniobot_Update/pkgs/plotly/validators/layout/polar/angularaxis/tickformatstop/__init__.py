

import _plotly_utils.basevalidators


class ValueValidator(_plotly_utils.basevalidators.StringValidator):

    def __init__(
        self,
        plotly_name='value',
        parent_name='layout.polar.angularaxis.tickformatstop',
        **kwargs
    ):
        super(ValueValidator, self).__init__(
            plotly_name=plotly_name,
            parent_name=parent_name,
            edit_type=kwargs.pop('edit_type', 'plot'),
            role=kwargs.pop('role', 'style'),
            **kwargs
        )


import _plotly_utils.basevalidators


class TemplateitemnameValidator(_plotly_utils.basevalidators.StringValidator):

    def __init__(
        self,
        plotly_name='templateitemname',
        parent_name='layout.polar.angularaxis.tickformatstop',
        **kwargs
    ):
        super(TemplateitemnameValidator, self).__init__(
            plotly_name=plotly_name,
            parent_name=parent_name,
            edit_type=kwargs.pop('edit_type', 'plot'),
            role=kwargs.pop('role', 'info'),
            **kwargs
        )


import _plotly_utils.basevalidators


class NameValidator(_plotly_utils.basevalidators.StringValidator):

    def __init__(
        self,
        plotly_name='name',
        parent_name='layout.polar.angularaxis.tickformatstop',
        **kwargs
    ):
        super(NameValidator, self).__init__(
            plotly_name=plotly_name,
            parent_name=parent_name,
            edit_type=kwargs.pop('edit_type', 'plot'),
            role=kwargs.pop('role', 'style'),
            **kwargs
        )


import _plotly_utils.basevalidators


class EnabledValidator(_plotly_utils.basevalidators.BooleanValidator):

    def __init__(
        self,
        plotly_name='enabled',
        parent_name='layout.polar.angularaxis.tickformatstop',
        **kwargs
    ):
        super(EnabledValidator, self).__init__(
            plotly_name=plotly_name,
            parent_name=parent_name,
            edit_type=kwargs.pop('edit_type', 'plot'),
            role=kwargs.pop('role', 'info'),
            **kwargs
        )


import _plotly_utils.basevalidators


class DtickrangeValidator(_plotly_utils.basevalidators.InfoArrayValidator):

    def __init__(
        self,
        plotly_name='dtickrange',
        parent_name='layout.polar.angularaxis.tickformatstop',
        **kwargs
    ):
        super(DtickrangeValidator, self).__init__(
            plotly_name=plotly_name,
            parent_name=parent_name,
            edit_type=kwargs.pop('edit_type', 'plot'),
            items=kwargs.pop(
                'items', [
                    {
                        'valType': 'any',
                        'editType': 'plot'
                    }, {
                        'valType': 'any',
                        'editType': 'plot'
                    }
                ]
            ),
            role=kwargs.pop('role', 'info'),
            **kwargs
        )
