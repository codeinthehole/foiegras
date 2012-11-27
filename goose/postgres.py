# Create a copy of a table schema
CREATE_TEMP_TABLE = (
    "CREATE TEMPORARY TABLE %(new_table)s "
    "AS TABLE %(source_table)s "
    "WITH NO DATA")

LOAD_CSV = "COPY %(table)s FROM '%(filepath)s' CSV"

UPDATE_SQL = (
    "UPDATE %(master)s "
    "SET %(columns)s "
    "USING %(temp)s "
    "WHERE %(keys)s")

def load(table_name, filepath, columns):

    # Create temp table
    temp_table_name = table_name + '_temp'
    sql = CREATE_TEMP_TABLE % {
        'new_table': temp_table_name,
        'source_table': table_name}

    # Load CSV into temporary table
    sql = LOAD_CSV(temp_table_name, filepath)

    # Maybe create indexes to speed up the join for the update operation

    # Determine unique keys on destination table

    # Copy data across into main table


