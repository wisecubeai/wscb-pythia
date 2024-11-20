# Databricks notebook source
# MAGIC %md
# MAGIC The next steps will help you create some records for a inference table. We are using a custon prompt format what use the question and context.
# MAGIC
# MAGIC Your workspace must have Unity Catalog enabled. (https://docs.databricks.com/en/machine-learning/model-serving/inference-tables.html)
# MAGIC
# MAGIC This function retrieves values from Databricks widgets, which you can set in the job UI or as widgets in a Databricks notebook:
# MAGIC
# MAGIC - api_key (string): Need to be provided as an databricks token if internal models are used or api_key if external like OpenAI.
# MAGIC - model_base_url (string): Default request url to Serving Endpoints (eg. https://dbc-{internal-id}.cloud.databricks.com/serving-endpoints)
# MAGIC - model_name (string): If the model used is a databrticks hosted model set model_name=databricks/any-model-on-databricks.

# COMMAND ----------

from openai import OpenAI


# COMMAND ----------

dbutils.widgets.text("api_key", "")
dbutils.widgets.text("model_name", "")
dbutils.widgets.text("model_base_url", "")


api_key = dbutils.widgets.get("api_key")
model_name = dbutils.widgets.get("model_name")
model_base_url = dbutils.widgets.get("model_base_url")

# COMMAND ----------

sample_data = [
  ("What are the genetic or protein targets associated with metastatic melanoma?","Uveal melanoma (UM) is the most common primary intraocular malignancy in the adult eye. Despite the aggressive local management of primary UM, the development of metastases is common with no effective treatment options for metastatic disease. Genetic analysis of UM samples reveals the presence of mutually exclusive activating mutations in the Gq alpha subunits GNAQ and GNA11. One of the key downstream targets of the constitutively active Gq alpha subunits is the protein kinase C (PKC) signaling pathway. Herein, we describe the discovery of darovasertib (NVP-LXS196), a potent pan-PKC inhibitor with high whole kinome selectivity. The lead series was optimized for kinase and off target selectivity to afford a compound that is rapidly absorbed and well tolerated in preclinical species. LXS196 is being investigated in the clinic as a monotherapy and in combination with other agents for the treatment of uveal melanoma (UM), including primary UM and metastatic uveal melanoma (MUM)."),

  ("What are the potential molecular targets implicated in the pathogenesis of SARS-CoV-2?","The pathogenic mechanisms and immune response of COVID-19 are far from clear. Through a documentary review of literature, the authors describe virological and molecular aspects of SARS-CoV-2, the intimate mechanisms of cell infection, and potential therapeutic targets. They also analyze the characteristics of immune response of the infected subject. Objectives of this study are to describe the state of knowledge on virological data, molecular and physiopathogenic mechanisms of SARS-CoV-2, with a view to a better understanding of the therapeutic targets, as well as the immune response of the infected subject. Reported data could contribute to a better understanding of molecular mechanisms of cellular infection by SARS-CoV-2 as well as to a more easy explanation of the action of pharmacological agents used for the treatment, while elucidating intimate mechanisms of the immunity of infected subject."),
  ("Were any dose-limiting toxicities observed during the clinical trial for breast cancer?", "Breast cancer cells disseminate to distant sites via Tumor Microenvironment of Metastasis (TMEM) doorways. The TIE2 inhibitor rebastinib blocks TMEM doorway function in the PyMT mouse model of breast cancer. We aimed to assess the safety and pharmacodynamics of rebastinib plus paclitaxel or eribulin in patients with HER2-negative metastatic breast cancer (MBC). This phase Ib trial enrolled 27 patients with MBC who received 50 mg or 100 mg of rebastinib PO BID in combination with weekly paclitaxel 80 mg/m2 (if ≤ 2 prior non-taxane regimens) or eribulin 1.4 mg/m2 on days 1 & 8 (if ≥ 1 prior regimen). Safety, tolerability and pharmacodynamic parameters indicating TIE2 kinase inhibition and TMEM doorway function were evaluated. No dose-limiting toxicities in cycle 1 or 2 were observed among the first 12 patients at either rebastinib dose level. The most common treatment-emergent adverse events (AEs) were anemia (85%), fatigue (78%), anorexia (67%), leukopenia (67%), increased alanine aminotransferase (59%), hyperglycemia (56%), nausea (52%), and neutropenia (52%). AEs attributed to rebastinib include muscular weakness and myalgias. Intraocular pressure increased at the 100 mg rebastinib dose level, whereas angiopoietin-2 levels increased at both dose levels, providing pharmacodynamic evidence for TIE2 blockade. Circulating tumor cells decreased significantly with the combined treatment. Objective response occurred in 5/23 (22%) evaluable patients. In patients with MBC, the recommended phase 2 dose of rebastinib associated with pharmacodynamic evidence of TIE2 inhibition is either 50 or 100 mg PO BID in combination with paclitaxel or eribulin."),

  ("What are the current ongoing or completed clinical trials for X?", "Nonalcoholic fatty liver disease (NAFLD) represents an increasingly recognized disease entity with rising prevalence of 25% in the general population. Given the epidemic increase, regulatory agencies have defined an unmet medical need and implemented initiatives to expedite the development of drugs for NASH treatment. Literature search in Medline and worldwide web was accessed latest in 23.01.2021. In recent years new drugs acting on various pathophysiological processes in NASH have entered clinical development. These drugs combine beneficial metabolic effects with anti-inflammatory and anti-fibrotic effects to treat NASH. Current drug classes being investigated for NASH treatment are agonists of nuclear receptors such as FXR agonists (including FGF19), PPAR agonists, chemokine receptor inhibitors, thyroid hormone receptor-ß agonists and analogues of enterohepatic hormones including GLP-1 and FGF21 or SGLT2 inhibitors. Obeticholic acid is the only drug with significant benefit in the phase 3 interim results and remains the candidate for first conditional approval as a NASH therapeutic. However, monotherapy with these drugs leads to a histological resolution of NASH in less than one-third of patients in recent trials. Therefore, the future of NASH therapy will putatively be a combination therapy of two different drug classes with complementary effects."), 
  
  ("What are the reported adverse events associated with drug X?", "To assess the relationships among quetiapine blood concentration, daily dose, dopamine receptor occupancy, and clinical outcome in order, if possible, to define a target plasma level range in which therapeutic response is enhanced and adverse events are minimized. A search of the database Embase from 1974 to March 2009 and the databases MEDLINE and PubMed from 1966 to March 2009 was conducted. The drug name quetiapine was searched with each of the terms plasma levels, plasma concentration, therapeutic drug monitoring, and dopamine occupancy. The search uncovered 42 relevant articles. All published reports of quetiapine plasma or serum concentration were considered for inclusion if reported in relation to a dose, clinical outcome, or dopamine occupancy. After application of exclusion criteria, 20 articles remained. Trials designed primarily to investigate an interaction between quetiapine and another medication were excluded, as were those designed to compare methods of blood sample analysis. There was a weak correlation between quetiapine dose and measured plasma concentration (from trough samples). Quetiapine dose was correlated with central dopamine D(2) occupancy, although the relationship between plasma level and D(2) occupancy is less clear. The dose-response relationship for (immediate-release) quetiapine is established. Data on plasma concentration-response relationships are not sufficiently robust to allow determination of a therapeutic plasma level range for quetiapine. Therapeutic drug monitoring procedures are thus probably not routinely useful in optimizing quetiapine dose. Further examination of the relationship between peak quetiapine plasma concentration and clinical response is necessary.")

]

# COMMAND ----------

def create_prompt(question, context):
  return """{}\nContext: \n{}
  """.format(question, context)

# COMMAND ----------

client = OpenAI(
  api_key=api_key, # your personal access token
  base_url=model_base_url
)

# COMMAND ----------

def call_databricks(prompt, model, key, base_url):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant that can use Context to answer questions",
            },
            {"role": "user", "content": prompt},
        ],
        model=model,
        max_tokens=256,
    )

# COMMAND ----------

# MAGIC %md
# MAGIC We will call the model for witch we had enable the inference. The result will might appear just after a period of time not instant.

# COMMAND ----------

for sample in sample_data:
  prompt = create_prompt(sample[0], sample[1])
  call_databricks(prompt=prompt, model=model_name, key=api_key, base_url=model_base_url)