from typing import Optional, Literal, Tuple, Iterator
from datetime import datetime
import json
import uuid
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
from mysql.connector import MySQLConnection
from google.cloud import secretmanager
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas_gbq
import pandas as pd
from src.sql_template import *
from src.properties import table_properties_mysql2bq, CARD


def get_secret(
    project_id: str, secret_id: str, key_path: str, version: str = "latest"
) -> json:
    """retrieve google cloud secret"""

    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    credentials = service_account.Credentials.from_service_account_file(key_path)
    secret_client = secretmanager.SecretManagerServiceClient(credentials=credentials)
    response = secret_client.access_secret_version(request={"name": secret_name})
    payload = response.payload.data.decode("UTF-8")

    return json.loads(payload)


def connect2mysql(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> Engine:
    """enter credentials to return mySQL engine object."""

    connect_url = URL.create(
        "mysql+mysqlconnector",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
    )

    return create_engine(connect_url, connect_args={"connect_timeout": 500})


def mysql2df(
    sql: str,
    engine: Engine,
    chunksize: int = None,
) -> pd.DataFrame | Iterator[pd.DataFrame]:
    """extract data from MySQL in dataframe or generator"""

    conn: MySQLConnection = engine.connect()
    generator_df = pd.read_sql(sql=sql, con=conn, chunksize=chunksize)

    return generator_df


def df2bq(
    df: pd.DataFrame,
    table_name: table_properties_mysql2bq,
    dataset_name: str,
    key_path: str,
) -> None:
    """save dataframe to bigquery"""

    credentials = service_account.Credentials.from_service_account_file(key_path)

    try:
        pandas_gbq.to_gbq(
            dataframe=df,
            destination_table=f"{table_name.dataset_id_bq}.{dataset_name}.{table_name.table_name_bq}",
            project_id=table_name.project_id_gc,
            # table_schema=table_name.schema_bq,
            if_exists="append",
            chunksize=None,
            api_method="load_csv",
            location="US",
            verbose=False,
            credentials=credentials,
        )
    except Exception as e:
        print("ERROR: " + str(e))


def count_row_sql(
    db_engine: Literal["mysql", "bigquery"],
    table_name: table_properties_mysql2bq,
    is_incremental: bool,
    dataset_name: str,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    count_distinct: Optional[bool] = False,
) -> str:
    """to fill in placeholders in sql templates,
    then count rows
    """

    if is_incremental and db_engine == "mysql":
        formatted_sql = MYSQL_INCREMENTAL_ROW_COUNT.format(
            database=table_name.database_name_mysql,
            table=table_name.table_name_mysql,
            updated_timestamp_col=table_name.updated_column,
            start_datetime_inclusive=start_datetime,
            end_datetime_exclusive=end_datetime,
        )
    elif is_incremental and db_engine == "bigquery":
        formatted_sql = BIGQUERY_INCREMENTAL_ROW_COUNT.format(
            distinct_pk=f"DISTINCT {table_name.primary_key_bq}"
            if count_distinct
            else "*",
            dataset_id=table_name.dataset_id_bq,
            dataset_name=dataset_name,
            table_name=table_name.table_name_bq,
            updated_timestamp_col=table_name.updated_column,
            start_datetime_inclusive=start_datetime,
            end_datetime_exclusive=end_datetime,
        )
    elif not is_incremental and db_engine == "mysql":
        formatted_sql = MYSQL_SNAPSHOT_ROW_COUNT.format(
            database=table_name.database_name_mysql,
            table=table_name.table_name_mysql,
        )
    elif not is_incremental and db_engine == "bigquery":
        formatted_sql = BIGQUERY_SNAPSHOT_ROW_COUNT.format(
            distinct_pk=f"DISTINCT {table_name.primary_key_bq}"
            if count_distinct
            else "*",
            dataset_id=table_name.dataset_id_bq,
            dataset_name=dataset_name,
            table_name=table_name.table_name_bq,
        )
    return formatted_sql


def execute_count_row(
    db_engine: Literal["mysql", "bigquery"],
    table_name: table_properties_mysql2bq,
    is_incremental: bool,
    dataset_name: str,
    engine: Optional[Engine] = None,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    count_distinct: Optional[bool] = False,
) -> int:
    """execute count_row_sql()"""

    sql = count_row_sql(
        db_engine,
        table_name,
        is_incremental,
        dataset_name,
        start_datetime,
        end_datetime,
        count_distinct,
    )

    if db_engine == "mysql":
        with engine.connect() as conn:
            df = pd.read_sql(sql, conn)
            row_count = df.iloc[0, 0]
    elif db_engine == "bigquery":
        df = pandas_gbq.read_gbq(sql, project_id=table_name.dataset_id_bq)
        row_count = df.iloc[0, 0]

    return row_count


def create_table_sql(
    table_name: table_properties_mysql2bq,
    dataset_name: str,
) -> str:
    """to generate sql query for creating BigQuery table
    - schema is specified in src/properties.py
    - the primary key is strictly not nullable
    """

    list_sql_string = []
    sql_syntax_bigquery = ""

    for key, val in table_name.schema_bq.items():
        sql_string = "`{key}` {val} {nullable}".format(
            key=key,
            val=val,
            nullable="NOT NULL" if key == table_name.primary_key_bq else "",
        )
        list_sql_string.append(sql_string)

    for x in list_sql_string:
        sql_syntax_bigquery += x + ",\n"

    formatted_sql = BIGQUERY_CREATE_TABLE.format(
        dataset_id=table_name.dataset_id_bq,
        dataset_name=dataset_name,
        table_name=table_name.table_name_bq,
        schema_bigquery=sql_syntax_bigquery,
    )
    return formatted_sql


def execute_create_table(
    table_name: table_properties_mysql2bq,
    dataset_name: str,
    key_path: str,
) -> None:
    """create a new table in BigQuery
    by executing create_table_sql()
    """

    sql = create_table_sql(table_name, dataset_name)

    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(
        credentials=credentials,
        project=credentials.project_id,
    )
    try:
        query_job = client.query(sql)
        print(query_job.result())
    except Exception as e:
        print("ERROR: " + str(e))


def select_mysql(
    table_name: table_properties_mysql2bq,
    is_incremental: bool,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    row_limit: Optional[int] = None,
) -> str:
    """to fill in placeholders in sql templates,
    then pull data from mysql
    """

    if row_limit:
        mysql_row_limit = f"LIMIT {row_limit}"

    if is_incremental:
        formatted_sql = MYSQL_INCREMENTAL_SELECT.format(
            schema_mysql=table_name.schema_mysql,
            table=table_name.table_name_mysql,
            database=table_name.database_name_mysql,
            row_limit=mysql_row_limit if row_limit else "",
            updated_timestamp_col=table_name.updated_column,
            start_datetime_inclusive=start_datetime,
            end_datetime_exclusive=end_datetime,
        )
    else:
        formatted_sql = MYSQL_SNAPSHOT_SELECT.format(
            schema_mysql=table_name.schema_mysql,
            table=table_name.table_name_mysql,
            database=table_name.database_name_mysql,
            row_limit=mysql_row_limit if row_limit else "",
        )

    return formatted_sql


def cloud_storage_prefix(
    table: table_properties_mysql2bq,
    bucket_name: str,
    environment: Literal["dev", "prod"],
    end_datetime: datetime,
) -> str:
    """generate an unique path to cloud storage for raw data"""

    gs_url = "gs://{bucket_name}/{environment}/{table_name}/year={year}/month={month}/day={day}/{filename}"
    filename = "{table_name}_{uuid}.csv"

    filename = filename.format(
        table_name=table.table_name_bq,
        uuid=uuid.uuid4(),
    )

    gs_url = gs_url.format(
        bucket_name=bucket_name,
        environment=environment,
        table_name=table.table_name_bq,
        year=end_datetime.year,
        month=end_datetime.month,
        day=end_datetime.day,
        filename=filename,
    )

    return gs_url


def process_chunk_then_load(
    df: pd.DataFrame,
    table_name: table_properties_mysql2bq,
    dataset_name: str,
    key_path: str,
    bucket_name: str,
    environment: Literal["dev", "prod"],
    end_datetime: datetime,
) -> None:
    """for each dataframe chunk:
    1. save raw data to cloud storage
    2. load to BigQuery
    """
    gs_url = cloud_storage_prefix(
        table=table_name,
        bucket_name=bucket_name,
        environment=environment,
        end_datetime=end_datetime,
    )
    df.to_csv(gs_url)
    print(f"Data saved in {gs_url} ...")

    df2bq(
        df=df,
        table_name=table_name,
        dataset_name=dataset_name,
        key_path=key_path,
    )
