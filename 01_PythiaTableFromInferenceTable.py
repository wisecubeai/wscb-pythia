# Databricks notebook source
# MAGIC %md
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC This function retrieves values from Databricks widgets, which you can set in the job UI or as widgets in a Databricks notebook:
# MAGIC
# MAGIC - api_key (string): Need to be provided as an databricks token if internal models are used or api_key if external like OpenAI. For databricks token go to **Settings->Developer->Access tokens**
# MAGIC - catalog (string): The catalog in which the Delta table for storing **Pythia** results is located.
# MAGIC - model_base_url (string): If the model used in **Pythia** is a Databrticks hosted model  set **model_name=databricks/any-model-on-databricks** as a prefix when sending litellm requests (https://docs.litellm.ai/docs/providers/databricks) (eg. https://dbc-{internal-id}.cloud.databricks.com/serving-endpoints)
# MAGIC - model_name (string): If the model used is a Databricks hosted model set model_name=databricks/{databricks_serving_model}
# MAGIC - schema (string): The schema that is storing **Pythia** Delta table.
# MAGIC - table_name (string): The name of the **Pythia** Delta table to store the hallucination detected statistics.
# MAGIC - refresh_interval (string) This should match the schedule interval of the workflow. Example values: "ALL", "DAILY", "HOURLY", "WEEKLY", "MONTHLY". This values are then converted to the expected SQL Query.

# COMMAND ----------

!pip install askpythia

# COMMAND ----------

# MAGIC %restart_python

# COMMAND ----------

from pythia.evaluators.models import HostedModel
from pythia.evaluators.strategies.pythiav1 import PythiaV1Evaluator
import os
import json

# COMMAND ----------

dbutils.widgets.text("api_key", "")
dbutils.widgets.text("model_name", "")
dbutils.widgets.text("model_base_url", "")
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "")
dbutils.widgets.text("table_name", "")
dbutils.widgets.text("refresh_interval", "")


api_key = dbutils.widgets.get("api_key")
model_name = dbutils.widgets.get("model_name")
model_base_url = dbutils.widgets.get("model_base_url")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
table_name = dbutils.widgets.get("table_name")
refresh_interval= dbutils.widgets.get("refresh_interval")

# COMMAND ----------

# MAGIC %md
# MAGIC We can use a list of specified refresh intervals to better controll the values allowed.
# MAGIC

# COMMAND ----------

valid_intervals = ["ALL", "DAILY", "HOURLY", "WEEKLY", "MONTHLY"] #. etc

# COMMAND ----------

if refresh_interval is None:
    refresh_interval = "ALL"
if len(refresh_interval)==0:
    refresh_interval = "ALL"
if refresh_interval not in valid_intervals:
    refresh_interval = "ALL"

refresh_interval

# COMMAND ----------

def generate_sql_query(schedule_type, catalog, schema, table_name):
    base_query = "SELECT * FROM {}.{}.`{}`".format(catalog, schema, table_name)
    
    if schedule_type == "ALL":
        return base_query
    elif schedule_type == "DAILY":
        # Filter by `date` for DAILY schedules
        return f"{base_query} WHERE CAST(date AS DATE) = CURRENT_DATE"
    elif schedule_type == "HOURLY":
        # Filter by `timestamp_ms` for HOURLY schedules (within the last hour)
        return f"""
        {base_query} 
        WHERE CAST(FROM_UNIXTIME(timestamp_ms / 1000) AS TIMESTAMP) >= DATE_SUB(NOW(), 1)
        """
    elif schedule_type == "WEEKLY":
        # Filter by `date` for WEEKLY schedules (current week)
        return f"""
        {base_query} 
        WHERE YEARWEEK(CAST(date AS DATE), 1) = YEARWEEK(CURRENT_DATE, 1)
        """
    elif schedule_type == "MONTHLY":
        # Filter by `date` for MONTHLY schedules (current month)
        return f"""
        {base_query} 
        WHERE YEAR(CAST(date AS DATE)) = YEAR(CURRENT_DATE)
        AND MONTH(CAST(date AS DATE)) = MONTH(CURRENT_DATE)
        """
    else:
        return "Invalid schedule type."

# COMMAND ----------

# MAGIC %md
# MAGIC Databricks Helper methods used to paste the Inference table content to suit the Pythia input.

# COMMAND ----------

def get_question_context_from_request(request_data):
    request_data = json.loads(request_data)
    str_data =  request_data["messages"][1]["content"]
    try:
        # Split the template text at the keyword "Context:"
        parts = str_data.split("Context:", 1)
    
        # Check if both parts (question and context) exist
        if len(parts) == 2:
            # Strip any extra whitespace and assign to dictionary keys
            return {
                "question": parts[0].strip(),
                "context": parts[1].strip()
            }
        else:
            #If there is No Context assume is only the question
            return {
                "question": str_data,
                'context': None
            }
    except Exception as e:
        print(e)
        return {
                "question": str_data,
                'context':None
                
            }

# COMMAND ----------

def get_model_response(response_data):
    try:
        response_data = json.loads(response_data)
        return response_data["choices"][0]["message"]["content"]
    except Exception as e:
        print(e)
        return "fail to get model response {}, type {}".format(e, type(response_data))

# COMMAND ----------

def pythia_summary(row):
    try:
        pythia_result = (
            row["databricks_request_id"],)
        # os.environ["OPENAI_API_KEY"] = api_key
        model = HostedModel(model=model_name, api_key=api_key, api_base=model_base_url)
        evaluator = PythiaV1Evaluator(model)
        model_response = row["response"]
        model_input = row["request"]
        response = get_model_response(response_data=model_response)
        qc = get_question_context_from_request(request_data=model_input)

        pythia_response = evaluator.evaluate_summary(
            summary=response,
            reference=qc["context"],
            question=qc["question"],
            validators_enabled=True,
        )
        response_dict = pythia_response.json()
        if type(response_dict) == str:
            response_dict = json.loads(response_dict)

        pythia_result += (
            float(response_dict["metrics"]["accuracy"]),
            float(response_dict["metrics"]["entailment"]),
            float(response_dict["metrics"]["contradiction"]),
            float(response_dict["metrics"]["neutral"]),
        )
        validator_result = []
        for validator_response in response_dict["validatorsResults"]:
            validator_result += [{
                "name": validator_response["validator"]["name"],
                "riskScore": float(validator_response["riskScore"]),
                "isValid": validator_response["isValid"],
                "errorMessage": ' '.join(str(validator_response["errorMessage"]).replace(", ", "").replace(",", ", ").split()),
            }]
        pythia_result += (validator_result, None)
        print(pythia_result)
        return pythia_result
    except Exception as e:
        return pythia_result + (0.0, 0.0, 0.0, 0.0, [], e)

# COMMAND ----------

# MAGIC %md
# MAGIC Use the connected inference table from the model serving endpoint to obtain the data required as input to run pythia

# COMMAND ----------

import nltk
nltk.download('punkt_tab')

# COMMAND ----------

# Create a widget to pass the query
dbutils.widgets.text("sql_query", generate_sql_query(schedule_type=refresh_interval, catalog=catalog, schema=schema, table_name=table_name))


# COMMAND ----------

# MAGIC %sql
# MAGIC ${sql_query}
# MAGIC

# COMMAND ----------

inference_df = _sqldf

# COMMAND ----------

inference_df.count()

# COMMAND ----------

inference_df.show()

# COMMAND ----------

rdd_transformed = inference_df.rdd.map(pythia_summary)

# COMMAND ----------

# Define the schema for the new DataFrame
from pyspark.sql.types import (
    StructType,
    StructField,
    FloatType,
    StringType,
    ArrayType,
    BooleanType,
)

output_schema = StructType(
    [
        StructField("databricks_request_id", StringType(), True),
        StructField("accuracy", FloatType(), True),
        StructField("entailment", FloatType(), True),
        StructField("contradiction", FloatType(), True),
        StructField("neutral", FloatType(), True),
        StructField(
            "validators",
            ArrayType(
                StructType(
                    [
                        StructField("name", StringType(), True),
                        StructField("riskScore", FloatType(), True),
                        StructField("isValid", BooleanType(), True),
                        StructField("errorMessage", StringType(), True),
                    ]
                )
            ),
            True,
        ),
        StructField("exception", StringType(), True),
    ]
)

# Convert the RDD back to a DataFrame with the new schema
try:
    df_new = spark.createDataFrame(rdd_transformed, schema=output_schema)
except Exception as e:
    print(f"Error creating DataFrame: {e}")
display(df_new)

# COMMAND ----------

output_table = f"{catalog}.{schema}.`{table_name}-pythia`"

# COMMAND ----------

output_table

# COMMAND ----------

write_mode = "append"
if refresh_interval == "ALL":
    write_mode = "overwrite"

# COMMAND ----------

df_new.write.format("delta").mode(write_mode).saveAsTable(output_table)