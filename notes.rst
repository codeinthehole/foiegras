Links:
http://www.postgresql.org/docs/8.3/static/populate.html

Notes:
COPY does not truncate - but fails on constraint violations
Faster to drop table indexes, then load, then create indexes
Maybe have class for CSV file

Comparison between MySQL/Postgres:
* COPY can't skip header lines

TODO
* CSV file
* Match COPY options 
