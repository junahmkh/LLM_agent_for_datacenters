import pandas as pd
import os
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, FOAF, XSD
import sys
import time
import pickle

inpts = sys.argv
year_month = str(inpts[1])

plugin = "job_table"
metric = "job_info_marconi100"

dir_path = "../data/year_month={}/".format(year_month)

#plugin_df = pd.read_csv("raw_data/plugins/{}.csv".format(plugin.split("_")[0]))

job_data = pd.read_parquet(os.path.join(dir_path,"plugin={}/metric={}/a_0.parquet".format(plugin,metric)))

columns_needed = ["job_id","nodes","start_time","end_time"]

def get_node(nodes_str):
    nodes_list = []
    tmp = nodes_str[1:-1]
    if ',' in tmp:
        tmp = tmp.split(",")
        for item in tmp:
            nodes_list.append(int(item))
    else:
        nodes_list.append(int(tmp))
    return nodes_list
   

# Define namespaces
m100 = Namespace("http://ontologies.metaphacts.com/cineca_m100/")  # Your namespace URI

# Initialize RDF graph
g = Graph()

g.bind("cineca_m100", m100)  # Bind the namespace to the variable name


"""
JOB instances
"""
# define job and its relation with node
for i in range(job_data.shape[0]):
    job = m100["job_{}".format(job_data['job_id'][i])]
    job_id = m100["jobId"]
    job_start_time = m100["startTime"]
    job_end_time = m100["endTime"]
    
    usesNode = m100["UsesNode"]

    # Add the triple to the graph
    g.add((job, RDF.type, m100["Job"]))
    g.add((job, job_id, Literal(job_data['job_id'][i],datatype=XSD.integer)))
    g.add((job, job_start_time, Literal(job_data['start_time'][i],datatype=XSD.dateTime)))
    g.add((job, job_end_time, Literal(job_data['end_time'][i],datatype=XSD.dateTime)))

    nodes_list = get_node(job_data['nodes'][idx])

    for node in nodes_list:
        g.add((job, usesNode, m100[f"node_{node}"]))


g.serialize(destination="job_data_{year_month}_{metric}.ttl")