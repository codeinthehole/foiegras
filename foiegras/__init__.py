import time

# Load CSV data into a table from a file
LOAD_CSV = """
    COPY %(table)s %(columns)s
    FROM '%(filepath)s'
    DELIMITER AS '%(delimiter)s'
    CSV %(options)s"""

# Duplicate a table's schema to form a new table without any data.
CREATE_TEMP_TABLE = """
    CREATE  TABLE %(temp)s
    AS TABLE %(base)s
    WITH NO DATA"""

# Convoluted query to fetch the indexes for a given table
# See http://stackoverflow.com/questions/2204058/show-which-columns-an-index-is-on-in-postgresql
# relkind = 'r' => ordinary table
GET_INDEXES = """
    SELECT
        a.attname AS column_name
    FROM
        pg_class t,
        pg_class i,
        pg_index ix,
        pg_attribute a
    WHERE
        t.oid = ix.indrelid
        AND i.oid = ix.indexrelid
        AND ix.indisunique = TRUE
        AND a.attrelid = t.oid
        AND a.attnum = ANY(ix.indkey)
        AND t.relkind = 'r'
        AND t.relname = '%(table)s'"""

# Update records in master table that match a uniqueness constraint with
# records in the temp table
UPDATE_MATCHES = """
    UPDATE %(base)s s
    SET %(set_fields)s
    FROM %(temp)s t
    WHERE %(where_sql)s"""

# Insert records from temp table that don't match a uniqueness constraint on
# the master table.
INSERT_NEW = """
    INSERT INTO %(base)s (%(destination_fields)s) (
        SELECT %(copy_fields)s
        FROM %(temp)s t
        LEFT JOIN %(base)s s
        ON %(join_sql)s
        WHERE s IS NULL
    )"""


class Goose(object):

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def load(self, table, filepath, fields=None,
             delimiter=",", replace_duplicates=True, has_header=False):
        temp_table = self._create_temp_table(table)
        self._load(temp_table, filepath, fields, delimiter, has_header)
        self._copy(table, temp_table, fields, replace_duplicates)
        self._drop(temp_table)
        self.connection.commit()

    def _drop(self, table):
        self.cursor.execute("DROP TABLE %s" % table)

    def _copy(self, table, source_table, fields,
              replace_duplicates):
        # Determine unique keys on master table.  We use these for the JOIN
        # query when copying data across.  We also add an index on these fields
        # to improve performance for the copy operation.
        unique_fields = self._unique_fields(table, fields)
        self._add_index(source_table, unique_fields)
        if replace_duplicates:
            self._update_matching_rows(
                table, source_table, fields, unique_fields)
        self._insert_new_rows(table, source_table, fields, unique_fields)

    def _add_index(self, table, fields):
        # We use a multi-column
        sql = "CREATE INDEX %(table)s_copy_ind ON %(table)s (%(fields)s)" % {
            'table': table,
            'fields': ", ".join(fields)}
        self.cursor.execute(sql)

    def _update_matching_rows(self, table, source_table, fields,
                              unique_fields):
        key_pairs = []
        for field in unique_fields:
            key_pairs.append("s.%(field)s = t.%(field)s" % {
                'field': field})
        where_sql = " AND ".join(key_pairs)

        copy_fields = set(fields).difference(unique_fields)
        set_pairs = []
        for field in copy_fields:
            set_pairs.append("%(field)s = t.%(field)s" % {
                'field': field})
        set_fields = ", ".join(set_pairs)

        sql = UPDATE_MATCHES % {
            'base': table,
            'temp': source_table,
            'set_fields': set_fields,
            'where_sql': where_sql}
        self.cursor.execute(sql)

    def _insert_new_rows(self, table, source_table, fields, unique_fields):
        copy_sql = ", ".join(map(lambda x: "t.%s" % x, fields))
        key_pairs = []
        for field in unique_fields:
            key_pairs.append("s.%(field)s = t.%(field)s" % {
                'field': field})
        join_sql = " AND ".join(key_pairs)
        sql = INSERT_NEW % {
            'base': table,
            'temp': source_table,
            'destination_fields': ", ".join(fields),
            'copy_fields': copy_sql,
            'join_sql': join_sql}
        self.cursor.execute(sql)

    def _create_temp_table(self, table):
        suffix = "_%10.6f" % time.time()
        name = table + suffix.replace('.', '_')
        sql = CREATE_TEMP_TABLE % {
            'temp': name,
            'base': table}
        self.cursor.execute(sql)
        return name

    def _load(self, table, filepath, fields, delimiter, has_header):
        """
        Load CSV data into a table
        """
        columns = ""
        if fields:
            columns = "(" + ", ".join(fields) + ")"
        sql = LOAD_CSV % {
            'table': table,
            'columns': columns,
            'delimiter': delimiter,
            'options': 'HEADER' if has_header else '',
            'filepath': filepath}
        self.cursor.execute(sql)

    def _unique_fields(self, table, fields):
        """
        Return the columns that have unique indexes from the passed
        table.
        """
        sql = GET_INDEXES % {
            'table': table
        }
        self.cursor.execute(sql)
        unique_cols = set([row[0] for row in self.cursor.fetchall()])
        return unique_cols.intersection(fields)
