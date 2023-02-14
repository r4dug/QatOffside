#!/usr/bin/env python
import snowflake.connector

# Gets the version
ctx = snowflake.connector.connect(
    user='R4DUG',
    password='WorldCup22',
    account='cy81590',
    database = 'QAT_OFFSIDE',
    warehouse = 'COMPUTE_WH',
    region = 'eu-central-1',
    schema = 'PUBLIC'
    )
cs = ctx.cursor()
try:
    cs.execute("SELECT current_version()")
    one_row = cs.fetchone()
    print(one_row[0])
finally:
    cs.close()
ctx.close()