# LLM_agent_for_datacenters
Project for the Knowledge engineering course at UNIBO by Junaid Ahmed Khan.

Collaborators: Prof. Andrea Bartolini (Supervisor) and Martin Molan.

## Introduction
Data centers have become essential to support the massive computational requirements of large language models (LLMs). As demand grows, so does the need for scalability in these data centers. However, with greater scalability comes increased complexity in managing such facilities. For example, CINECA’s Leonardo supercomputer consists of approximately 5,000 compute nodes and millions of sensors, all within a single facility. To address these challenges, data centers rely on Operational Data Analytics (ODA) practices, which provide insights to streamline management and ensure efficient performance at scale.

Operational Data Analytics (ODA) consists of two main components:

1. **Collection of Telemetry Data**: This involves gathering detailed telemetry data from the facility, including metrics from compute nodes, sensors, and other critical infrastructure.

2. **Monitoring Framework**: This component focuses on analyzing the collected data and providing visualizations to support informed decision-making and ensure efficient facility management.
The following figure outlines the typical data center facility with ODA:

![Data Center with ODA](images/datacenter_with_ODA.png)

## Problem Statement
Current approaches in data center and HPC data monitoring typically rely on NoSQL databases due to their scalability and ability to handle diverse data sources. However, this approach often results in telemetry data lacking a defined structure and relationships between different data sources. The absence of a clear structure requires domain knowledge of both the data center infrastructure and the collected data to manage it effectively. Furthermore, variability in data management practices across different data centers adds another layer of complexity to data analysis and interpretation.



![Ontology for Operational Data Analytics in Data centers](images/ontologyV1.7.png)

| **No.** | **Prompt**                                                                                  |
|---------|---------------------------------------------------------------------------------------------|
| 1       | Give me all the nodes present in rack 1                                                     |
| 2       | Give me a list of all the racks                                                             |
| 3       | Give me the position of node 3                                                              |
| 4       | Give me the list of plugins                                                                 |
| 5       | What nodes were used by the job 1001282?                                                    |
| 6       | What is the average power used by the job 1000882?                                          |
| 7       | How many jobs are running on node 5 during the month of May 2022?                           |
| 8       | What is the min, max, and avg temperature of node 5 when it is in use during May 2022?      |
| 9       | Give me a list of sensors which are of type "power"                                         |
| 10      | Give me a list of the jobs running and the nodes they used during the month of May 2022     |
