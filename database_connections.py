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

    print(f'Data already normalized from R...')
    # sc = StandardScaler()
    # sc_data = sc.fit_transform(data_values)
    # sc_data = data_values

    print(f'Fitting PCA...')
    sc_data = data_values
    pca = PCA(n_components=0.85)
    pca_data = pca.fit_transform(sc_data)

    # Exclude the first column (cell identifiers)
    # matrix_values = pca_data[:, 1:]

    # Extract gene expression values
    gene_values = pca_data[:, :].tolist()

    # Prepare data
    data = []
    max_vec_length = 5880
    for i, vals in enumerate(gene_values):

        # Insert data in chunks of 1000 to avoid sending too much data at once and Milvus rejecting it
        counter = 1000
        if i < counter:
            num_vals = len(vals)
            if num_vals < max_vec_length:
                to_add = max_vec_length - num_vals
                for _ in range(to_add):
                    vals.append(0.0)

            elif len(vals) > 1000:
                print(f'Vector size of {num_vals} > {max_vec_length}. Cannot upload to Milvus')

            # Create primary key
            primary_key = int(f'{experiment_num}00000')
            if i > 0:
                num_digits = math.floor(np.log10(i)) + 1
                primary_key = f'{experiment_num}'
                for _ in range(5 - num_digits):
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

        print(f'Sending rows {counter - 1000} to {counter} to Milvus...')
        res = client.insert(
            collection_name=collection_name,
            data=data
        )

    print(res)


def find_similarities(collection_name, root_vector_ids, limit=10):
    """
    This function will query the Milvus database for vectors that have the highest
        cosine similarity to the root vector.

    :param: collection_name: The name of the collection to query.
    :param root_vector_ids: The vector or list of vectors to find similarities to.
    :param limit: The number of similar vectors to find
    :return: A tuple where the first element is:
                A dictionary with keys [query_vector_id], where query_vector_id points to a
                list of (vector_id, cosine_similarity_value, filename) tuples
                ordered by most to least similar.
            And the second element is a list of file names the vectors originate from
    """

    # Ensure that root_vector_id is always a list
    if not isinstance(root_vector_ids, list):
        print(f'Error: root_vector_ids must be a list.')
        return

    print(f'** Finding similarities function **')

    # Set up a Milvus client
    print(f'Connecting to Milvus...')
    client = MilvusClient(uri=CLUSTER_ENDPOINT, token=TOKEN)

    # Get the root vectors from Milvus
    root_vector_ids.sort()
    print(f'Retrieving vectors...')
    res = client.get(collection_name=collection_name, ids=root_vector_ids)
    res.sort(key=lambda x: x['primary_key'], reverse=False)

    # Extract query vectors
    query_vectors = []
    for item in res:
        query_vectors.append(item['vector'])

    # Perform search
    print(f'Performing cosine similarity query...')
    res = client.search(
        collection_name=collection_name,  # target collection
        data=query_vectors,  # query vectors
        limit=limit,  # number of returned entities
        output_fields=['file_name']
    )

    # Process results
    print(f'Processing results...')
    output = {}
    filenames = set()
    for query in res:
        results = []
        for match in query:
            vector_id = match['id']  # Accessing the first element of the list
            cosine_similarity_value = match['distance']
            file_name = match['entity']['file_name']
            filenames.add(file_name)

            # Append the tuple (vector_id, cell_name, file_name, cosine_similarity_value) to the results list
            results.append((vector_id, cosine_similarity_value, file_name))

        # Sort results by cosine similarity value (descending order)
        results.sort(key=lambda x: x[1], reverse=True)

        output[query[0]['id']] = results

    return output, filenames
