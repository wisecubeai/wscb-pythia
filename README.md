## Pythia - AI Observability for Reliable Generative AI

Pythia is an AI observability and reliability platform designed to monitor and manage the outputs of Large Language Models (LLMs) in real-time. It ensures that your generative AI applications are accurate, fair, and trustworthy by detecting issues like hallucinations, bias, explainability gaps, and security vulnerabilities by seamlessly plugging into your existing observability stack.


## Reference Architecture

<img src=images/pythia_ai_hallucination_monitoring.png width="800px">

## Pythia in Databricks for Continuous Monitoring & Alerting

With Pythia, compliance is no longer a hurdle but a seamless aspect of your AI operations. Integration with Databricks monitoring and reporting not only helps you track and document your application's AI performance but also helps adhere to the highest standards of accountability and transparency.

<img src=images/pyhtia_wisecube_databricks_monitoring.png width="800px">

## Steps to build Monitoring and Alerting with Pythia in Databricks

1. Fisrt step is used to create some records with context as references that will be stored into a connected Databricks inference table that is associated directly to a Serving endpoint. We are using a custon prompt format what use the question and context. In order to proceed wiht that use the following notebook: [InputData notebook](00_PythiaExampleInput.py). Inference serving endpoint configuration template and also inference table that is associated are as per bellow screenshots:

#### Inference Serving Endpoint
   <img src=images/inference_serving_endpoint.png width="800px">
   
#### Inference table schema 
   <img src=images/inference_schema_details.png width="800px">

#### Inference table sample entries 
   <img src=images/inference_sample.png width="800px">

2. After the data from Serving Endpoints is stored into the reference table this can be then connected to the Pythia library to run and create statistics on it and save it back to a dedicated Databricks delta table into the existing Data Warehouse by following this notebook: [Pythia Hallucination Detection notebook](01_PythiaTableFromInferenceTable.py). There is also an important configiration related to the refresh interval and can be easy configured to run on different intervals. When all is configured correctly it will expose this type of statistics as presented in the table bellow:

#### Location of Access token for the serving endpoint
   <img src=images/access_token.png width="800px">
   
#### Table schema for pyhtia hallucination details including validators
  <img src=images/pythia_results.png width="800px">

| Validator name                         | description             | input      | output                                              |
|----------------------------------------|-------------------------|------------|-----------------------------------------------------|
| detect_pii                             | This scanner acts as your digital guardian, ensuring your user prompts remain confidential and free from sensitive data exposure. | input_reference | input_response |
| detect_prompt_injection                             | Guard against crafty input manipulations targeting LLM,by identifying and mitigating such attempts, it ensures the LLM operates securely without succumbing to injection attacks. | input_reference |  |
| detect_ban_substrings                             | Ensure that specific undesired substrings never make it into your prompts with the BanSubstrings scanner. |  | input_response |
| detect_gibberish                             | This scanner is designed to identify and filter out gibberish or nonsensical inputs in English language text. |  | input_response |
| detect_toxicity                             | This provides a mechanism to analyze and mitigate the toxicity of text content, this tool is instrumental in preventing the dissemination of harmful or offensive content. |  | input_response |
| detect_relevance                             | This scanner ensures that output remains relevant and aligned with the given input prompt. |  | input_response |
| detect_factual_consistency                             | This scanner is designed to assess if the given content contradicts or refutes a certain statement or prompt. It acts as a tool for ensuring the consistency and correctness of language model outputs, especially in contexts where logical contradictions can be problematic. |  | input_response |
| detect_secrets                             | This scanner diligently examines user inputs, ensuring that they don't carry any secrets before they are processed by the language model. |  | input_response |

3. Last step is to create the monitoring dashboard and to expose statistics based on the generated output from Pythia that will contain accuracy based on different types of detecion that was done on the input data from the inference tables into the dedicated Databricks Data Warehouse Delta table: [Monitoring and Alerting notebook](02_CreateTimeSeriesMonitor.py)

  <img src=images/databricks_dashboard_monitoring.png width="800px">

| Authors |
| ----------- |
| Databricks Inc. |
| WiseCube AI |

## Project support 

Please note the code in this project is provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs). They are provided AS-IS and we do not make any guarantees of any kind. Please do not submit a support ticket relating to any issues arising from the use of these projects. The source in this project is provided subject to the Databricks [License](./LICENSE.md). All included or referenced third party libraries are subject to the licenses set forth below.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo. They will be reviewed as time permits, but there are no formal SLAs for support. 

## License

&copy; 2024 Databricks, Inc. All rights reserved. The source in this notebook is provided subject to the Databricks License [https://databricks.com/db-license-source].  All included or referenced third party libraries are subject to the licenses set forth below.

| library                                | description             | license    | source                                              |
|----------------------------------------|-------------------------|------------|-----------------------------------------------------|
| askpythia                              | Advanced hallucination detection library to ensure your AI systems are both reliable and compliant, enhancing accuracy across all your Generative AI applications | MIT License | https://pypi.org/project/askpythia/ |
