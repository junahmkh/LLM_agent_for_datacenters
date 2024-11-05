import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from utils import *

# Function to run SPARQL query
def run_sparql_query(endpoint, query, username=None, password=None):
    headers = {'Accept': 'application/sparql-results+json'}
    response = requests.post(endpoint, data={'query': query}, headers=headers,
                             auth=(username, password) if username and password else None)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

# Function to get query output as a pandas DataFrame
def query_output(graphdb_endpoint, sparql_query, username=None, password=None):
    results = run_sparql_query(graphdb_endpoint, sparql_query, username, password)
    columns = results['head']['vars']
    data = [
        [result[col]['value'] if col in result else None for col in columns]
        for result in results["results"]["bindings"]
    ]
    df = pd.DataFrame(data, columns=columns)
    return df