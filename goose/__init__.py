LOAD_CSV = "COPY %(table)s %(columns)s FROM '%(filepath)s' CSV"


class Goose(object):

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def load(self, table, filepath, fields=None):
        columns = ""
        if fields:
            columns = "(" + ", ".join(fields) + ")"
        sql = LOAD_CSV % {
            'table': table,
            'columns': columns,
            'filepath': filepath}
        self.cursor.execute(sql)
        self.connection.commit()
