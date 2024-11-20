# Databricks notebook source
# MAGIC %md
# MAGIC This Notebook sets up monitoring for a Delta table in Databricks, enabling time-series data quality checks with specified granularity. It is designed to use Databricks job parameters to dynamically specify the target table, user workspace, timestamp column, and granularity.
# MAGIC Purpose
# MAGIC
# MAGIC The create_delta_table_monitor function creates a quality monitor for a specified Delta table. It allows tracking changes and monitoring data quality over time, saving the necessary monitoring assets in the user’s workspace. The function uses the timestamp_col to set the monitoring intervals based on the specified granularity.
# MAGIC Parameters
# MAGIC
# MAGIC This function retrieves values from Databricks widgets, which you can set in the job UI or as widgets in a Databricks notebook:
# MAGIC
# MAGIC - catalog (string): The catalog in which the Delta table is located.
# MAGIC - schema (string): The schema containing the Delta table.
# MAGIC - table_name (string): The name of the Delta table to be monitored.
# MAGIC - user_email (string): User’s email to specify where the assets are stored in the workspace.
# MAGIC - ts_column (string): Timestamp column to base the time-series monitoring.
# MAGIC - granularity (string, optional): Monitoring interval granularity (default: "30 minutes").

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import MonitorSnapshot


# COMMAND ----------

 # Define widgets for each parameter
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "")
dbutils.widgets.text("table_name", "")
dbutils.widgets.text("user_email", "")
    
    # Retrieve widget values
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
table_name = dbutils.widgets.get("table_name")
user_email = dbutils.widgets.get("user_email")


# COMMAND ----------

def create_delta_table_monitor(catalog, schema, table_name, user_email):
    """
    Creates a monitoring setup for a specified Delta table in Databricks, enabling time-series monitoring for data quality checks.

    This method sets up a quality monitor for a given Delta table, storing monitoring assets in the user’s workspace.
    The monitor tracks changes and quality metrics in the table using the specified timestamp column and granularities.

    Parameters:
        catalog (str): The catalog in which the Delta table is located.
        schema (str): The schema containing the Delta table.
        table_name (str): The name of the Delta table to be monitored.
        user_email (str): The email of the user (used to determine the workspace path for saving assets).
        ts_column (str): The name of the timestamp column used for time-series monitoring.
        granularity (str): The granularity for time-series monitoring (default is "30 minutes").

    Returns:
        None
    """

    # Initialize the Databricks Workspace client
    workspace_client = WorkspaceClient()

    # Create quality monitor for the specified Delta table
    w = WorkspaceClient()
    w.quality_monitors.create(
        table_name=f"{catalog}.{schema}.{table_name}",
        assets_dir=f"/Workspace/Users/{user_email}/databricks_lakehouse_monitoring/{catalog}.{schema}.{table_name}",
        output_schema_name=f"{catalog}.{schema}",
        snapshot=MonitorSnapshot()
    )

# COMMAND ----------

create_delta_table_monitor(
    catalog=catalog,
    schema=schema,
    table_name=table_name,
    user_email=user_email
)