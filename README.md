
    +------------------+
    |          __      | FOIE GRAS
    | uh oh >(' )      | The missing CSV loading library for Postgres
    |         )/       |
    |        /(        |
    |       /  `----/  |
    |       \  ~=- /   |
    | ~^~^~^~^~^~^~^~^ |
    +----------------- +

In MySQL you can do this:

    mysql> LOAD DATA INFILE '/tmp/data.csv'
        -> REPLACE INTO TABLE 'my_data'
        -> FIELDS (isbn, price, stock);

to load data from a CSV file into a table, replacing rows that match on a unique constraint.  
This is not possible in Postgres...

...until now:

    $ pip install foiegras 
    $ python
    >>> import psycopg2, foiegras
    >>> conn = psycopg2.connect("dbname=mydb")
    >>> goose = foiegras.Goose(conn)
    >>> goose.load('my_data', '/tmp/data.csv', ('isbn', 'price', 'stock'))

Yay!

## Interesting... tell me more

The Postgres equivalent of [`LOAD DATA INFILE`](http://dev.mysql.com/doc/refman/5.1/en/load-data.html) 
is the [`COPY ... FROM ...`](http://www.postgresql.org/docs/9.2/static/sql-copy.html)
command, however it does not support replacing rows that match on a unique
constraint.  Using CSVs to load data into a table is the fastest way of
updating a table - hence it's frustrating that Postgres doesn't
support the `REPLACE` option that MySQL does.

This package works around this issue by loading the CSV to a temporary table then 
updating the master table using two `UPDATE` commmands that insert new records and update
matching records respectively.  All very simple.

Further reading:

* [Relevant Stack Overflow question](http://stackoverflow.com/questions/8910494/how-to-update-selected-rows-with-values-from-a-csv-file-in-postgres)
* [Wiki page for COPY](http://www.postgresql.org/docs/9.2/static/sql-copy.html)
* [Populating a database](http://www.postgresql.org/docs/8.3/static/populate.html)

## Surely this has been done already?

Apparently not.  There are some similar CSV loading libraries for Django

* [`django-csvimport`](http://pypi.python.org/pypi/django-csvimport) - This is a Django
  app for uploading CSV files to populate model tables.  It uses the ORM directly to save
  new instances and so does not perform well when loading larges volumes of data.

* [pgloader](http://pgfoundry.org/projects/pgloader/) - This looks like it might be quite good 
  but it's hard to tell as the docs are so bad.  It's also not on PyPI.
