## Pythia - AI Observability for Reliable Generative AI

Pythia is an AI observability and reliability platform designed to monitor and manage the outputs of Large Language Models (LLMs) in real-time. It ensures that your generative AI applications are accurate, fair, and trustworthy by detecting issues like hallucinations, bias, explainability gaps, and security vulnerabilities by seamlessly plugging into your existing observability stack.


## Reference Architecture

<img src=images/pythia_ai_hallucination_monitoring.png width="800px">

## Pythia in Databricks for Continuous Monitoring & Alerting

With Pythia, compliance is no longer a hurdle but a seamless aspect of your AI operations. Integration with Databricks monitoring and reporting not only helps you track and document your application's AI performance but also helps adhere to the highest standards of accountability and transparency.

<img src=images/pyhtia_wisecube_databricks_monitoring.png width="800px">

## Steps to build Monitoring and Alerting with Pythia in Databricks

1. Fisrt step is used to create some records with context as references that will be stored into a connected Databricks inference table that is associated directly to a Serving endpoint. We are using a custon prompt format what use the question and context. In order to proceed wiht that use the following notebook: [InputData notebook](00_PythiaExampleInput.py)

2. After the data from Serving Endpoints is stored into the reference table this can be then connected to the Pythia library to run and create statistics on it and save it back to a dedicated Databricks delta table into the existing Data Warehouse by following this notebook: [Pythia Hallucination Detection notebook](01_PythiaTableFromInferenceTable.py)

3. Last step is to create the monitoring dashboard and to expose statistics based on the generated output from Pythia into the dedicated Databricks Data Warehouse Delta table: [Monitoring and Alerting notebook](02_CreateTimeSeriesMonitor.py)

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
| askpythia                              | Advanced hallucination detection API to ensure your AI systems are both reliable and compliant, enhancing accuracy across all your Generative AI applications | MIT License | https://pypi.org/project/askpythia/ |
