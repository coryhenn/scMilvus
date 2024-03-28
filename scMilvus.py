import os

from pymilvus import MilvusClient
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

CLUSTER_ENDPOINT = "http://localhost:19530"
TOKEN = "YOUR_CLUSTER_TOKEN"

# Set up a Milvus client
# client = MilvusClient(uri=CLUSTER_ENDPOINT, token=TOKEN)

# Read data from CSV file
path = os.path.join('data', 'output_matrix.csv')
data = pd.read_csv(path, delimiter=',')

print(data.head)

data_values = data.iloc[:, 1:].values

sc = StandardScaler()
sc_data = sc.fit_transform(data_values)

pca = PCA(n_components=0.85)
pca_data = pca.fit_transform(sc_data)


# Exclude the first column (cell identifiers)
#matrix_values = pca_data[:, 1:]

# Extract gene expression values
gene_values = pca_data[:, :].tolist()
print(gene_values[0])
exit(0)

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

# collection_name="Exp1scRNAseq",
# dimension=32286
# )
