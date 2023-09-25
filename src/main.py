from typing import Optional, Literal
import types
from datetime import datetime, timedelta
import argparse
import warnings
import src.properties as properties
from src.properties import table_properties_mysql2bq, mySQL_tables
from src.etl import *

PROJECT_ID = "<gcp-project-num>"
SECRET_ID = "<gcp-secret-id>"
KEY_PATH = "./<gcp-key-name>.json"
CHUNK_THRESHOLD = 50000
BUCKET_NAME = "etl-raw-data"


def run_etl(
    environment: Literal["dev", "prod"],
    table_name: table_properties_mysql2bq,
    start_datetime: datetime,
    end_datetime: datetime,
    is_incremental: bool = True,
    row_limit: int = None,
) -> None:
    """
    run etl functions step by step
    """

    warnings.filterwarnings("ignore")

    # step 0:
    #
    #       retrieve credentials for mySQL
    #       from google cloud secret manager
    credentials = get_secret(
        project_id=PROJECT_ID, secret_id=SECRET_ID, key_path=KEY_PATH
    )

    # step 1:
    #
    #       for snapshot ingestion only
    #       create a new table with fixed schema in BigQuery
    if not is_incremental:
        execute_create_table(
            table_name=table_name,
            dataset_name=f"schema_{environment}",
            key_path=KEY_PATH,
        )

    # step 2:
    #
    #       format sql query template
    sql = select_mysql(
        table_name=table_name,
        is_incremental=is_incremental,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        row_limit=row_limit,
    )

    engine = connect2mysql(
        host=credentials["HOST"],
        port=credentials["PORT"],
        user=credentials["USER"],
        password=credentials["PASSWORD"],
        database=credentials["DATABASE"],
    )

    # step 3:
    #
    #       get row count for mySQL raw data
    row_count_mysql = execute_count_row(
        db_engine="mysql",
        table_name=table_name,
        is_incremental=is_incremental,
        dataset_name=f"schema_{environment}",
        engine=engine,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        count_distinct=False,
    )
    print(f"row count: {row_count_mysql}")

    # step 4:
    #
    #       calculate if need to ingest in chunks
    if row_count_mysql > CHUNK_THRESHOLD:
        chunksize = CHUNK_THRESHOLD
    else:
        chunksize = None

    # step 5:
    #
    #       return dataframe (or generator) after selecting from mySQL
    dfs = mysql2df(
        sql=sql,
        engine=engine,
        chunksize=chunksize,
    )

    # step 6:
    #
    #       process data and then load to BigQuery
    if isinstance(dfs, types.GeneratorType):
        print("Processing data chunk by chunk ...")
        for df in dfs:
            process_chunk_then_load(
                df=df,
                table_name=table_name,
                dataset_name=f"schema_{environment}",
                key_path=KEY_PATH,
                bucket_name=BUCKET_NAME,
                environment=environment,
                end_datetime=end_datetime,
            )
    else:
        process_chunk_then_load(
            df=dfs,
            table_name=table_name,
            dataset_name=f"schema_{environment}",
            key_path=KEY_PATH,
            bucket_name=BUCKET_NAME,
            environment=environment,
            end_datetime=end_datetime,
        )

    print(
        f"{table_name.dataset_id_bq}.schema_{environment}.{table_name.table_name_bq} saved."
    )

    # step 7:
    #
    #       get row count for distinct BigQuery records
    row_count_bq = execute_count_row(
        db_engine="bigquery",
        table_name=table_name,
        is_incremental=is_incremental,
        dataset_name=f"schema_{environment}",
        engine=engine,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        count_distinct=True,
    )
    print(
        f"Fetched {row_count_mysql} rows. Loaded {row_count_bq} distinct rows to BigQuery."
    )


def getArgs():
    parser = argparse.ArgumentParser(
        description="Get user input to run the right ETL pipeline."
    )
    parser.add_argument(
        "-env",
        "--environment",
        action="store",
        required=True,
        type=str,
        choices=("dev", "prod"),
        help="dev|prod, select development or production running environment.",
    )
    parser.add_argument(
        "-snapshot",
        action="store_true",
        help="Flag for full snapshot ingestion. If not provided, default is incremental ingestion.",
    )
    parser.add_argument(
        "-tbl",
        "--table",
        required=True,
        type=str,
        choices=[
            mySQL_tables.TABLE1.value,
            mySQL_tables.TABLE2.value,
        ],
        help="Enter one table name to run ETL.",
    )
    parser.add_argument(
        "-t0",
        "--start_datetime",
        type=str,
        help="Enter the start datetime in yyyy-mm-dd format, e.g. 2023-08-27. Default value is system date - 1 days.",
    )
    parser.add_argument(
        "-t1",
        "--end_datetime",
        type=str,
        help="Enter the end datetime in yyyy-mm-dd format, e.g. 2023-08-28. Default value is system date.",
    )
    return parser.parse_args()


def getTimeRange(
    start_date_str: Optional[str] = None, end_date_str: Optional[str] = None
) -> Tuple[datetime, datetime]:
    """default end datetime will be the system date
    default start datetime will be one days before system date
    reset time to 0
    """
    if start_date_str:
        start_datetime_inclusive = datetime.strptime(start_date_str, "%Y-%m-%d")
    else:
        start_datetime_inclusive = datetime.today() - timedelta(days=1)

    if end_date_str:
        end_datetime_exclusive = datetime.strptime(end_date_str, "%Y-%m-%d")
    else:
        end_datetime_exclusive = datetime.today()

    return (
        start_datetime_inclusive.replace(hour=0, minute=0, second=0, microsecond=0),
        end_datetime_exclusive.replace(hour=0, minute=0, second=0, microsecond=0),
    )


if __name__ == "__main__":
    arg = getArgs()

    STR_START_DATETIME = arg.start_datetime
    STR_END_DATETIME = arg.end_datetime
    ENVIRONMENT = arg.environment
    TABLE = getattr(properties, str(mySQL_tables(arg.table)))

    start_datetime, end_datetime = getTimeRange(STR_START_DATETIME, STR_END_DATETIME)

    if arg.snapshot:
        IS_INCREMENTAL = False
        print(
            f"""Creating a snapshot for {TABLE.table_name_bq} as of {end_datetime}."""
        )
    else:
        IS_INCREMENTAL = True
        print(
            f"""Running ETL for {TABLE.table_name_bq} from {start_datetime} to {end_datetime}."""
        )

    run_etl(
        environment=ENVIRONMENT,
        table_name=TABLE,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        is_incremental=IS_INCREMENTAL,
        row_limit=None,
    )
    print("End.")
