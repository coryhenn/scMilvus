from pymilvus import MilvusClient
import numpy as np
import pandas as pd

CLUSTER_ENDPOINT = "http://localhost:19530"
TOKEN = "YOUR_CLUSTER_TOKEN"

# 1. Set up a Milvus client
client = MilvusClient(
    uri=CLUSTER_ENDPOINT,
    token=TOKEN
)

data = pd.read_csv('output_matrix.csv', delimiter=',')

print(data.head)

# Extract gene names (column headers) as metadata
#gene_names = list(data.columns[1:])

# Extract gene expression values for the second row (excluding the first column)
gene_values = data.iloc[1, 1:].tolist()

# Define the id value
id_value = 0

# Construct the desired format as a dictionary
result = {
    "id": id_value,
    "vector": gene_values
}

# Print the result
print(result)

# 2. Create a collection in quick setup mode
# client.create_collection(

# collection_name="PoolAscRNAseq",
# dimension=32286
# )
