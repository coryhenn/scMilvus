"""
Contains function that query our Milvus collections
"""
import math
import os
import re

import numpy as np
import pandas as pd
from pymilvus import MilvusClient, DataType
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from global_variables import TOKEN, CLUSTER_ENDPOINT

# Todo: Jason


def insert_data(collection_name, filename):
    """
    This function will read a cell/gene matrix and perform the following:
        1. Read the data into memory
        2. Normalize the data to have mean 0, standard deviation 1.
        3. Fit a PCA that keeps 85% of the variance.
        4. Pad the PCA vector with zeroes so it is 1000 elements long.
        5. Send the PCA vector to Milvus along with the cell name, file name
            the data came from, and cell id (i.e. the index into the list
            of PCA vectors)
        For the cell_id, use the following convention:
            100000 where:
                - The first digit is the experiment number
                - The remaining 5 digits are reversed for cell_ids within the experiment.
                 i.e. cell id 0 will look like 100000, cell_id 1 = 100001,
                 cell_id 2 = 100002

    :param collection_name: The name of the Milvus cloud collection to be inserted to.
    :param: filename: The file in the data directory that contains the cell/gene matrix
        to be inserted into the collection.
    :return: 0 on success, 1 on failure (data could not be sent to Milvus)
    """

    # Set up a Milvus client
    print(f'Connecting to Milvus...')
    client = MilvusClient(uri=CLUSTER_ENDPOINT, token=TOKEN)

    # Read data from CSV file
    experiment_num = int(re.search(r'ex_\d+_', filename).group()[3:-1])
    print(f'Loading data from experiment {experiment_num}...')
    path = os.path.join('data', filename)
    data = pd.read_csv(path, delimiter=',')
    data_values = data.iloc[:, 1:].values

    print(f'Normalizing data...')
    sc = StandardScaler()
    sc_data = sc.fit_transform(data_values)

    print(f'Fitting PCA...')
    pca = PCA(n_components=0.85)
    pca_data = pca.fit_transform(sc_data)

    # Exclude the first column (cell identifiers)
    # matrix_values = pca_data[:, 1:]

    # Extract gene expression values
    gene_values = pca_data[:, :].tolist()

    # Prepare data
    data = []
    for i, vals in enumerate(gene_values):
        num_vals = len(vals)
        if num_vals < 1000:
            to_add = 1000 - num_vals
            for _ in range(to_add):
                vals.append(0.0)

        elif len(vals) > 1000:
            print(f'Vector size of {num_vals} > 1000. Cannot upload to Milvus')

        # Create primary key
        primary_key = 100000
        if i > 0:
            num_digits = math.floor(np.log10(i)) + 1
            primary_key = f'{experiment_num}'
            for _ in range(5-num_digits):
                primary_key += '0'
            primary_key += f'{i}'
            primary_key = int(primary_key)

        row_data = {
            'primary_key': primary_key,
            'vector': vals,
            'cell_name': 'na',
            'file_name': filename
        }

        data.append(row_data)

    print('Sending data to Milvus...')
    res = client.insert(
        collection_name=collection_name,
        data=data
    )

    print(res)

# exit(0)
#
# # Define the id value
# id_value = 0
#
# # Construct the desired format as a dictionary
# result = {
#     "id": id_value,
#     "vector": gene_values
# }
#
# # Print the result
# print(result)
#
# # 2. Create a collection in quick setup mode
# # client.create_collection(
#
# # collection_name="Exp1scRNAseq",
# # dimension=32286
# # )

# Todo: Cory


def find_similarities(collection_name, root_vector_id, limit, query_vectors):
    """
    This function will query the Milvus database for vectors that have the highest
        cosine similarity to the root vector.

    :param: collection_name: The name of the collection to query.
    :param root_vector_id: The vector or list of vectors to find similarities to.
    :param limit: The number of similar vectors to find
    :return: A dictionary with keys [filenames, results], where results is a
        list of (vector_id, cell_name, filename, cosine_similarity_value) tuples
        ordered by most to least similar. And filenames is a list of the
        files the vectors originated from.
    """

    # Ensure that root_vector_id is always a list
    if not isinstance(root_vector_id, list):
        root_vector_id = [root_vector_id]

    print(f'** Finding similarities function **')

    # Set up a Milvus client
    print(f'Connecting to Milvus...')
    client = MilvusClient(uri=CLUSTER_ENDPOINT, token=TOKEN)

    # Prepare query vectors
    query_vectors = root_vector_id

    # Start search
    res = client.search(
        collection_name="Cell_PCA",        # target collection
        data=query_vectors,                # query vectors
        limit=5,                           # number of returned entities
    )

    # Process search results
    results = []
    origin_files = set()

    for entity in res:
        vector_id = entity[0]  # Accessing the first element of the list
        cosine_similarity_value = entity[1]

        # Accessing the cell_name and file_name from the Milvus vector
        cell_name = entity['cell_name']
        file_name = entity['file_name']

        # Append the tuple (vector_id, cell_name, file_name, cosine_similarity_value) to the results list
        results.append(
            (vector_id, cell_name, file_name, cosine_similarity_value))
        origin_files.add(file_name)

    # Sort results by cosine similarity value (descending order)
    results.sort(key=lambda x: x[3], reverse=True)

    # Create a dictionary with keys "file_name" and "results"
    output = {"filenames": origin_files, "results": results}

    # Print the dictionary
    print(output)
