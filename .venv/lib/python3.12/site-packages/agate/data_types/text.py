from agate.data_types.base import DataType


class Text(DataType):
    """
    Data representing text.

    :param cast_nulls:
        If :code:`True`, values in :data:`.DEFAULT_NULL_VALUES` will be
        converted to `None`. Disable to retain them as strings.
    """
    def __init__(self, cast_nulls=True, **kwargs):
        super().__init__(**kwargs)

        self.cast_nulls = cast_nulls

    def cast(self, d):
        """
        Cast a single value to :func:`unicode` (:func:`str` in Python 3).

        :param d:
            A value to cast.
        :returns:
            :func:`unicode` (:func:`str` in Python 3) or :code:`None`
        """
        if d is None:
            return d
        if isinstance(d, str):
            if self.cast_nulls and d.strip().lower() in self.null_values:
                return None

        return str(d)
