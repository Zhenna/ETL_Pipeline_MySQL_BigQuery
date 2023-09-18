MYSQL_SNAPSHOT_SELECT = """
SELECT {schema_mysql}
FROM {database}.{table}
{row_limit}
"""

MYSQL_INCREMENTAL_SELECT = """
SELECT {schema_mysql}
FROM {database}.{table}
WHERE {updated_timestamp_col} >= '{start_datetime_inclusive}'
AND {updated_timestamp_col} < '{end_datetime_exclusive}'
{row_limit}
"""

MYSQL_SNAPSHOT_ROW_COUNT = """
SELECT COUNT(*)
FROM {database}.{table}
"""

MYSQL_INCREMENTAL_ROW_COUNT = """
SELECT COUNT(*)
FROM {database}.{table}
WHERE {updated_timestamp_col} >= '{start_datetime_inclusive}'
AND {updated_timestamp_col} < '{end_datetime_exclusive}'
"""

BIGQUERY_CREATE_TABLE = """
CREATE OR REPLACE TABLE `{dataset_id}.{dataset_name}.{table_name}` 
({schema_bigquery});
"""

BIGQUERY_SNAPSHOT_ROW_COUNT = """
SELECT COUNT({distinct_pk}) 
FROM `{dataset_id}.{dataset_name}.{table_name}` 
"""

BIGQUERY_INCREMENTAL_ROW_COUNT = """
SELECT COUNT({distinct_pk}) 
FROM `{dataset_id}.{dataset_name}.{table_name}` 
WHERE {updated_timestamp_col} >= '{start_datetime_inclusive}'
AND {updated_timestamp_col} < '{end_datetime_exclusive}'
"""
