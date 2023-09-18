from typing import Optional
from enum import Enum
from dataclasses import dataclass


@dataclass
class table_properties_mysql2bq:
    """standardized schema mapping structure
    for ETL pipeline from mySQL to BigQuery
    """

    table_name_mysql: str
    table_name_bq: str
    schema_mysql: str
    schema_bq: dict = None
    updated_column: Optional[str] = None
    primary_key_bq: Optional[str] = None
    database_name_mysql: str = "default_db"
    dataset_id_bq: str = "default_gcp_project"
    project_id_gc: str = "default_gcp_project_num"


class mySQL_tables(Enum):
    """all mySQL tables that have been tested
    for this ETL pipeline
    """

    TABLE1 = "table1"
    TABLE2 = "table2"

    def __str__(self):
        return self.name


TABLE1 = table_properties_mysql2bq(
    table_name_mysql="table1",
    table_name_bq="table_one",
    schema_mysql="""id,
    Status,
    created,
    updated,
    deleted,
    name,
    `default`""",
    schema_bq={
        "id": "STRING",
        "Status": "STRING",
        "created": "TIMESTAMP",
        "updated": "TIMESTAMP",
        "deleted": "TIMESTAMP",
        "name": "STRING",
        "default": "INTEGER",
    },
    updated_column="updated",
    primary_key_bq="id",
)

TABLE2 = table_properties_mysql2bq(
    table_name_mysql="table2",
    table_name_bq="table_two",
    schema_mysql="""id,
    Status,
    created, 
	updated, 
    `index`,
    content""",
    schema_bq={
        "id": "STRING",
        "Status": "STRING",
        "created": "TIMESTAMP",
        "updated": "TIMESTAMP",
        "index": "STRING",
        "content": "STRING",
    },
    updated_column="updated",
    primary_key_bq="id",
)
