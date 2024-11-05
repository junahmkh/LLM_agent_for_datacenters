import pandas as pd
import os
from datetime import datetime
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, FOAF, XSD
import sys
import time
import pickle

inpts = sys.argv
metric = str(inpts[1])
year_month = str(inpts[2])
start_idx = int(inpts[3])
end_idx = int(inpts[4])

dir_path = "../data/m100_3to12/year_month={}/".format(year_month)

plugin = "ipmi_pub"
plugin_df = pd.read_csv("raw_data/plugins/{}.csv".format(plugin.split("_")[0]))

node_data = pd.read_parquet(os.path.join(dir_path,"plugin={}/metric={}/a_0.parquet".format(plugin,metric)))

# Define namespaces
m100 = Namespace("http://cineca.com/exadata/m100/")  # Your namespace URI

# Initialize RDF graph
g = Graph()

g.bind("m100", m100)  # Bind the namespace to the variable name

#Load the RDF ontology from a .ttl file
#file_path = "m100_v1.6.ttl"  # Replace with the path to your .ttl file
#g.parse(file_path, format="ttl")  # Parse the .ttl file and load it into the graph

"""
IPMI instances
"""
# define plugin and its relation with node
for i in range(980):
    ipmi_pub = m100["ipmi_node_{}".format(i)]
    PluginName = m100["pluginName"]
    # Add the triple to the graph
    g.add((ipmi_pub, RDF.type, m100["Plugin"]))
    g.add((ipmi_pub, PluginName, Literal(plugin,datatype=XSD.string)))

    node = m100["node_{}".format(i)]
    hasPlugin = m100["HasPlugin"]

    # Node to plugin relation
    g.add((node, hasPlugin, ipmi_pub))

# Define the Sensor instances and their properties
for i in range(980):
    # sensor_metric_node
    sensor = m100["sensor_{}_{}".format(metric,i)]
    sensorName = m100["sensorName"]
    sensorType = m100["sensorType"]

    idx = plugin_df[plugin_df['Metric'] == metric].index[0]
    unit_idx = plugin_df["Unit"][idx]
    type_idx = plugin_df["type"][idx]
    # Add triples for the Sensor instance properties
    g.add((sensor, RDF.type, m100["Sensor"]))
    g.add((sensor, sensorName, Literal(metric,datatype=XSD.string)))
    g.add((sensor, sensorType, Literal(type_idx,datatype=XSD.string)))

    # Plugin to sensor relation
    g.add((m100["ipmi_node_{}".format(i)], m100["HasSensor"], sensor))

# Define DataRecord instance and its properties
record = m100[f"record_{year_month}/{plugin}/{metric}/"]
DataRecord = m100["DataRecord"]
fileName = m100["fileName"]
startTimestamp = m100["startTimestamp"]
endTimestamp = m100["endTimestamp"]

# Add triples for the instance properties
g.add((record, RDF.type, DataRecord))
g.add((record, fileName, Literal("a_0.parquet")))
g.add((record, startTimestamp, Literal(node_data['timestamp'][0], datatype=XSD.dateTime)))
g.add((record, endTimestamp, Literal(node_data['timestamp'][node_data.shape[0]-1], datatype=XSD.dateTime)))

start_time = time.perf_counter()
# Define the SensorReading instances and their properties
for idx in range(start_idx,end_idx):
    value_idx = node_data.iloc[idx]
    timestamp_idx = value_idx['timestamp']
    node_idx = value_idx['node']
    reading_idx = value_idx['value']
    #print(timestamp,node,value)

    # Parse the timestamp string into a datetime object
    dt_object = datetime.strptime(str(timestamp_idx), "%Y-%m-%d %H:%M:%S%z")
    # Convert the datetime object to a Unix timestamp
    unix_timestamp = int(dt_object.timestamp())

    # Deresults/{year_month}/{plugin}/{metric}/{start_idx}_{end_idx}fine the triple
    # metric_node_timestamp
    reading = m100["{}_{}_{}".format(metric,node_idx,unix_timestamp)]
    sensorReading = m100["SensorReading"]
    value = m100["value"]
    timestamp = m100["timestamp"]
    unit = m100["unit"]

    # Add the triple to the graph
    g.add((reading, RDF.type, sensorReading))
    g.add((reading, value, Literal(reading_idx, datatype=XSD.float)))
    g.add((reading, timestamp, Literal(timestamp_idx, datatype=XSD.dateTime)))
    g.add((reading, unit, Literal(unit_idx)))

    # Sensor to reading relation
    g.add((m100[f"sensor_{metric}_{node_idx}"], m100["HasReading"], reading))

    g.add((reading, m100["IsPartOf"], record))

end_time = time.perf_counter()
# Calculate the elapsed time
elapsed_time = end_time - start_time

time_path = "time_results"
if not os.path.exists(time_path):
    # Create a new directory because it does not exist
    os.makedirs(time_path)
    print("Time directory is created!")

with open(f"time_results/{year_month}_{plugin}_{metric}.pickle",'wb') as f:
    pickle.dump((elapsed_time,node_data.shape[0]),f)

# Save the graph to a .ttl file
save_path = f"results/{year_month}/{plugin}/{metric}"  # Replace with the desired output file path
if not os.path.exists(save_path):
    # Create a new directory because it does not exist
    os.makedirs(save_path)
    print("The new directory is created!")

g.serialize(destination=save_path+f"/{start_idx}_{end_idx}.ttl")