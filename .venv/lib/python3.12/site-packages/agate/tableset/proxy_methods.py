def bins(self, *args, **kwargs):
    """
    Calls :meth:`.Table.bins` on each table in the TableSet.
    """
    return self._proxy('bins', *args, **kwargs)


def compute(self, *args, **kwargs):
    """
    Calls :meth:`.Table.compute` on each table in the TableSet.
    """
    return self._proxy('compute', *args, **kwargs)


def denormalize(self, *args, **kwargs):
    """
    Calls :meth:`.Table.denormalize` on each table in the TableSet.
    """
    return self._proxy('denormalize', *args, **kwargs)


def distinct(self, *args, **kwargs):
    """
    Calls :meth:`.Table.distinct` on each table in the TableSet.
    """
    return self._proxy('distinct', *args, **kwargs)


def exclude(self, *args, **kwargs):
    """
    Calls :meth:`.Table.exclude` on each table in the TableSet.
    """
    return self._proxy('exclude', *args, **kwargs)


def find(self, *args, **kwargs):
    """
    Calls :meth:`.Table.find` on each table in the TableSet.
    """
    return self._proxy('find', *args, **kwargs)


def group_by(self, *args, **kwargs):
    """
    Calls :meth:`.Table.group_by` on each table in the TableSet.
    """
    return self._proxy('group_by', *args, **kwargs)


def homogenize(self, *args, **kwargs):
    """
    Calls :meth:`.Table.homogenize` on each table in the TableSet.
    """
    return self._proxy('homogenize', *args, **kwargs)


def join(self, *args, **kwargs):
    """
    Calls :meth:`.Table.join` on each table in the TableSet.
    """
    return self._proxy('join', *args, **kwargs)


def limit(self, *args, **kwargs):
    """
    Calls :meth:`.Table.limit` on each table in the TableSet.
    """
    return self._proxy('limit', *args, **kwargs)


def normalize(self, *args, **kwargs):
    """
    Calls :meth:`.Table.normalize` on each table in the TableSet.
    """
    return self._proxy('normalize', *args, **kwargs)


def order_by(self, *args, **kwargs):
    """
    Calls :meth:`.Table.order_by` on each table in the TableSet.
    """
    return self._proxy('order_by', *args, **kwargs)


def pivot(self, *args, **kwargs):
    """
    Calls :meth:`.Table.pivot` on each table in the TableSet.
    """
    return self._proxy('pivot', *args, **kwargs)


def select(self, *args, **kwargs):
    """
    Calls :meth:`.Table.select` on each table in the TableSet.
    """
    return self._proxy('select', *args, **kwargs)


def where(self, *args, **kwargs):
    """
    Calls :meth:`.Table.where` on each table in the TableSet.
    """
    return self._proxy('where', *args, **kwargs)
