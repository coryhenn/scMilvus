"""
Contains function that query our Milvus collections
"""

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
def insert_data(collection_name, filepath):
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
    :param: filepath: The file in the data directory that contains the cell/gene matrix
        to be inserted into the collection.
    :return: 0 on success, 1 on failure (data could not be sent to Milvus)
    """
    pass

# # Set up a Milvus client
# # client = MilvusClient(uri=CLUSTER_ENDPOINT, token=TOKEN)
#
# # Read data from CSV file
# path = os.path.join('data', 'output_matrix.csv')
# data = pd.read_csv(path, delimiter=',')
#
# print(data.head)
#
# data_values = data.iloc[:, 1:].values
#
# sc = StandardScaler()
# sc_data = sc.fit_transform(data_values)
#
# pca = PCA(n_components=0.85)
# pca_data = pca.fit_transform(sc_data)
#
#
# # Exclude the first column (cell identifiers)
# #matrix_values = pca_data[:, 1:]
#
# # Extract gene expression values
# gene_values = pca_data[:, :].tolist()
# print(gene_values[0])
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

