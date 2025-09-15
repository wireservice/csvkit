import os


def to_csv(self, dir_path, **kwargs):
    """
    Write each table in this set to a separate CSV in a given
    directory.

    See :meth:`.Table.to_csv` for additional details.

    :param dir_path:
        Path to the directory to write the CSV files to.
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    for name, table in self.items():
        path = os.path.join(dir_path, '%s.csv' % name)

        table.to_csv(path, **kwargs)
