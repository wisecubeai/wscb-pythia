# Databricks notebook source
# MAGIC %md
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC This function retrieves values from Databricks widgets, which you can set in the job UI or as widgets in a Databricks notebook:
# MAGIC
# MAGIC - api_key (string): Need to be provided as an databricks token if internal models are used or api_key if external like OpenAI.
# MAGIC - catalog (string): The catalog in which the Delta table for storing **Pythia** results is located.
# MAGIC - model_base_url (string): If the model used in **Pythia** is a Databrticks hosted model  set **model_name=databricks/any-model-on-databricks** as a prefix when sending litellm requests (https://docs.litellm.ai/docs/providers/databricks) (eg. https://dbc-{internal-id}.cloud.databricks.com/serving-endpoints)
# MAGIC - model_name (string): If the model used is a Databricks hosted model set model_name=databricks/{databricks_serving_model}
# MAGIC - schema (string): The schema that is storing **Pythia** Delta table.
# MAGIC - table_name (string): The name of the **Pythia** Delta table to store the hallucination detected statistics.

# COMMAND ----------

!pip install askpythia

# COMMAND ----------

# MAGIC %restart_python

# COMMAND ----------

from pythia.evaluators.models import HostedModel
from pythia.evaluators.strategies.pythiav2 import PythiaV2Evaluator
import os
import json

# COMMAND ----------

dbutils.widgets.text("api_key", "")
dbutils.widgets.text("model_name", "")
dbutils.widgets.text("model_base_url", "")
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "")
dbutils.widgets.text("table_name", "")

api_key = dbutils.widgets.get("api_key")
model_name = dbutils.widgets.get("model_name")
model_base_url = dbutils.widgets.get("model_base_url")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
table_name = dbutils.widgets.get("table_name")

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
        # os.environ["OPENAI_API_KEY"] = api_key
        model = HostedModel(model=model_name,api_key=api_key, api_base=model_base_url)
        evaluator = PythiaV2Evaluator(model)
        model_response = row["response"]
        model_input = row["request"]
        response = get_model_response(response_data=model_response)
        qc = get_question_context_from_request(request_data=model_input)
        
        pythia_response = evaluator.evaluate_summary(summary=response, reference=qc["context"], question=qc["question"])
        response_dict = pythia_response.json()
        
        return (response_dict["metrics"]["accuracy"],
                response_dict["metrics"]["entailment"],
                response_dict["metrics"]["contradiction"],
                response_dict["metrics"]["neutral"]
       
                )
    except Exception as e:
        return (None,None,None,None)
    
    


# COMMAND ----------

# MAGIC %md
# MAGIC Use the connected inference table from the model serving endpoint to obtain the data required as input to run pythia

# COMMAND ----------

inference_df = spark.sql("SELECT * FROM {}.{}.`{}`".format(catalog, schema, table_name))

# COMMAND ----------

inference_df.show(n=5)

# COMMAND ----------

inference_df.count()

# COMMAND ----------

rdd_transformed = inference_df.rdd.map(pythia_summary)

# COMMAND ----------

# Define the schema for the new DataFrame
from pyspark.sql.types import StructType, StructField, FloatType, StringType

output_schema = StructType([
    StructField("accuracy", FloatType(), True),
    StructField("entailment", FloatType(), True),
    StructField("contradiction", FloatType(), True),
    StructField("neutral", FloatType(), True)

])



# Convert the RDD back to a DataFrame with the new schema
df_new = spark.createDataFrame(rdd_transformed, schema=output_schema)
display(df_new)

# COMMAND ----------

output_table = f"{catalog}.{schema}.`{table_name}-pythia`"

# COMMAND ----------

output_table

# COMMAND ----------

df_new.write.format("delta").mode("overwrite").saveAsTable(output_table)