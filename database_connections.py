"""
Contains function that query our Milvus collections
"""
import os

import pandas as pd
from pymilvus import MilvusClient
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from global_variables import TOKEN, CLUSTER_ENDPOINT

# Todo: Cory
def find_similarities(collection_name, root_vector_id, top_n):
    """
    This function will query the Milvus database for vectors that have the highest
        cosine similarity to the root vector.

    :param: collection_name: The name of the collection to query.
    :param root_vector_id: The vector to find similarities to.
    :param top_n: The number of similar vectors to find
    :return: A dictionary with keys [filenames, results], where results is a
        list of (vector_id, cell_name, filename, cosine_similarity_value) tuples
        ordered by most to least similar. And filenames is a list of the
        files the vectors originated from.
    """
    pass


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
    pass

    # Set up a Milvus client
    client = MilvusClient(uri=CLUSTER_ENDPOINT, token=TOKEN)

    # Read data from CSV file
    path = os.path.join('data', filename)
    data = pd.read_csv(path, delimiter=',')

    print(data.head)

    data_values = data.iloc[:, 1:].values

    sc = StandardScaler()
    sc_data = sc.fit_transform(data_values)

    pca = PCA(n_components=0.85)
    pca_data = pca.fit_transform(sc_data)

    # Exclude the first column (cell identifiers)
    matrix_values = pca_data[:, 1:]

    # Extract gene expression values
    gene_values = pca_data[:, :].tolist()
    print(gene_values[0])

    # Prepare data
    data = []
    for i, vals in enumerate(gene_values):
        print(i, data)
        break

    #     {"id": 0, "vector": [0.3580376395471989, -0.6023495712049978, 0.18414012509913835, -
    #     0.26286205330961354, 0.9029438446296592], "color": "pink_8682"},
    #     {"id": 1, "vector": [0.19886812562848388, 0.06023560599112088, 0.6976963061752597,
    #                          0.2614474506242501, 0.838729485096104], "color": "red_7025"},
    #     {"id": 2, "vector": [0.43742130801983836, -0.5597502546264526, 0.6457887650909682,
    #                          0.7894058910881185, 0.20785793220625592], "color": "orange_6781"},
    #     {"id": 3, "vector": [0.3172005263489739, 0.9719044792798428, -
    #     0.36981146090600725, -0.4860894583077995, 0.95791889146345], "color": "pink_9298"},
    #     {"id": 4, "vector": [0.4452349528804562, -0.8757026943054742, 0.8220779437047674,
    #                          0.46406290649483184, 0.30337481143159106], "color": "red_4794"},
    #     {"id": 5, "vector": [0.985825131989184, -0.8144651566660419, 0.6299267002202009,
    #                          0.1206906911183383, -0.1446277761879955], "color": "yellow_4222"},
    #     {"id": 6, "vector": [0.8371977790571115, -0.015764369584852833, -
    #     0.31062937026679327, -0.562666951622192, -0.8984947637863987], "color": "red_9392"},
    #     {"id": 7, "vector": [-0.33445148015177995, -0.2567135004164067, 0.8987539745369246,
    #                          0.9402995886420709, 0.5378064918413052], "color": "grey_8510"},
    #     {"id": 8, "vector": [0.39524717779832685, 0.4000257286739164, -0.5890507376891594, -
    #     0.8650502298996872, -0.6140360785406336], "color": "white_9381"},
    #     {"id": 9, "vector": [0.5718280481994695, 0.24070317428066512, -0.3737913482606834, -
    #     0.06726932177492717, -0.6980531615588608], "color": "purple_4976"}
    # ]
    return
    # 4.2. Insert data
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

