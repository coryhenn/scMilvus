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

# Todo: Jason: Figure out a way to get the vector info. Seperate query?
def find_similarities(collection_name, root_vector_id, limit):
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

    query_vectors = [[-9.265895, -5.5149455, -6.028198, 0.4282228, 0.40608868, 10.280198, -2.175723, 1.9342839,
                     -6.313365, 6.681499, -11.720432, -3.1693964, -11.184838, 9.932231, 7.657586, -1.007327, 9.932082,
                     -19.768759, 4.6492167, -3.600245, 5.551393, 7.065084, 8.820168, -6.6726947, -1.6543552, -6.7104793,
                     -7.382901, 1.7338569, -7.9954777, -8.787629, -6.5378747, -3.3785872, -7.5078983, 1.4295937,
                     -6.9581156, -0.9336959, -3.7653224, 4.5435824, -3.415903, -2.4653668, -9.258948, -0.61850613,
                     7.8686566, -3.7043085, -2.576087, 12.16212, -5.0351663, 4.0551906, -6.616707, -3.4958673, -10.4634,
                     -3.8955743, -2.0793262, -8.01817, -3.0289814, -8.090793, 12.578454, 1.2692815, 5.1502695,
                     -14.400114, -11.756797, -6.924902, 2.044404, -2.6153224, -5.998015, 12.75727, -2.8404467, 12.69925,
                     5.9729214, 8.9735985, -9.232893, 7.3598413, 6.4789376, 2.4531856, -8.743463, -18.799393,
                     -1.7735366, 5.7254267, -10.905441, -16.065765, 13.098307, -8.240086, 8.350833, -7.138867,
                     -13.655522, 8.443044, 2.0964942, -3.8784661, -0.14751343, 1.9958867, 15.052701, 12.075295,
                     -1.961912, 4.5023046, 7.164231, -11.201796, -4.7704372, -15.126431, -5.901091, 3.9993584,
                     0.60995746, 0.9488883, 1.704323, -13.16107, 1.3311236, -11.320522, -11.754755, 12.413078,
                     11.744762, -9.48435, -9.301229, 2.429009, -1.4800293, -3.7218118, -13.843669, 13.4118395,
                     -6.4255104, 1.6924764, 5.6715584, -2.4214518, -7.023078, 12.823336, 2.703772, -7.656695, 6.626818,
                     -11.237097, 2.5455358, -12.426422, -2.8173854, -9.430328, -4.049585, 9.976354, -6.291233,
                     -8.433472, -4.989125, 7.4620166, -1.4841915, -2.079055, 0.57879263, 13.5842285, 2.3121214,
                     -11.379554, 8.502404, 5.9573627, 0.3801155, 4.7630386, 3.4300761, 6.2354727, -6.3507605, -10.11436,
                     -6.081976, 6.296726, 9.164332, -4.5238204, -13.640608, -5.4185944, -2.0232944, -8.107724,
                     -2.7302501, 11.419406, -11.68905, 5.7529864, -16.375486, 1.2617061, -0.9065905, -3.326074,
                     4.3404727, -1.0018781, 2.3622522, 15.193428, 10.329625, 5.4363933, 14.5617285, 2.543325, 6.6639295,
                     -6.257436, 5.5440025, 3.233623, -7.2767644, 6.2841277, -3.1456816, -4.293617, 5.7291355, 2.376726,
                     9.633501, 5.400606, 17.041481, 6.0541487, 6.7700233, 11.631194, 2.916112, 16.014793, 5.1502104,
                     8.105514, 3.521656, 4.546001, -2.063514, -0.7118097, 0.63701177, 4.3096175, -19.376268, -1.107996,
                     -7.7030754, -13.692234, 10.144101, 4.414049, 5.0952287, 1.9962268, -4.607799, -11.174291,
                     -3.338628, 8.327718, -12.405409, -9.359255, 4.733328, 5.384618, -3.0358467, 1.7034837, -9.019135,
                     2.7318635, -2.765628, 3.9726124, 13.134796, 2.3843243, -6.1812744, 2.0069358, 10.704934, 6.2702384,
                     -14.418084, -3.307576, 8.321065, -10.752033, -4.7082214, 5.282633, 11.07313, -8.822886, -3.3621988,
                     -15.947415, 10.109037, -8.122228, 0.6481969, -5.6684885, -1.9937413, 15.066867, -0.13477054,
                     -4.067649, 0.11214632, 22.801142, -7.331627, 13.141412, 8.977751, -1.6984468, 3.799654, -4.4355183,
                     3.5384836, -5.9504747, -0.6016382, -5.3686604, -3.7653825, -11.405671, -11.940423, -3.4096227,
                     2.4662735, -4.37477, -6.3700356, -14.805738, -2.5220113, 3.527467, 15.2928705, 3.258621,
                     -5.1499367, 15.638935, -1.3889357, -2.6477118, 1.8770585, 4.395277, 4.9249797, 2.2405875,
                     -0.32543617, 13.301166, -7.468731, -9.5437975, 1.7933326, -7.8609443, -7.372676, -8.266519,
                     -4.424685, -5.1954236, -6.283467, -1.5133343, -4.5881305, -6.478216, 2.2690399, -13.236443,
                     3.1508253, -4.020742, -8.916636, -9.9120655, -3.8894377, -1.9314516, -8.910076, -4.639497,
                     -5.057798, -4.3913617, 16.847385, -0.082092136, 13.282793, -9.029854, -7.0765653, -2.7896445,
                     12.742231, -0.057679743, -0.5352657, 0.27618062, 16.126999, -0.31730026, -5.6893334, 2.6119163,
                     4.1804957, 1.800281, -2.0931087, -8.226665, 4.0507207, -5.661996, 5.3324375, -7.583431, -7.97056,
                     -0.8412049, 5.5176983, 11.487245, 4.34711, 0.37150735, -2.8319232, 3.347996, 5.0645823, 4.107359,
                     5.126651, 8.5075245, 8.991187, -5.6457505, -4.0781264, 18.932066, -4.29816, 11.699307, 0.4735201,
                     2.7580469, 1.343085, 0.87179565, 11.481743, 4.819956, -7.4116855, 12.529908, 9.940547, -8.481493,
                     11.500839, -2.628475, -2.4046698, 4.9706564, 0.5801914, 9.156565, 5.0312634, -0.8846773,
                     -17.225353, -5.1206536, -13.140171, -10.657193, -0.19596131, 4.421383, -13.258458, -13.111384,
                     2.023149, 1.2965124, -4.883848, 2.0170949, -1.8495908, -2.963122, -7.640071, -7.167793, -3.0649273,
                     4.1115294, -0.8539157, -0.65102106, 5.608576, 11.038436, -5.6266513, -8.508817, 7.133376,
                     -5.354989, -5.1136255, 13.117693, -17.351706, 6.770949, -5.26951, 4.28513, -4.6945214, 4.625953,
                     4.569039, 3.4416645, 8.404037, 0.16778064, 3.4350948, -5.2201242, 0.79046535, -3.8035977, 0.852403,
                     -6.6296444, -2.166353, -11.830395, -4.424035, 1.1432003, 13.039541, -11.872227, -5.0377736,
                     5.260067, -2.9744086, 6.826425, -13.366969, -2.8967285, -4.619694, 3.377199, -5.8217463, 10.066634,
                     -0.92172307, -0.062558554, -7.9892087, -3.9238365, 7.8716936, -0.47210333, -5.8305664, -4.688213,
                     -10.137881, -7.041397, 14.339263, -4.4120135, -2.4934356, 2.1474667, -7.3670583, 4.7260423,
                     -5.946052, -1.4128432, -10.6429205, 3.8601072, 2.2147064, -3.150541, 4.6435175, 3.6182234,
                     -2.2455895, 13.311642, 3.203457, 17.453075, 0.35899267, -4.339643, 8.620207, 1.9007368,
                     -0.05971443, 6.5501075, 14.939989, -1.2283462, -6.8891306, 2.7691605, 3.6856987, -0.91010857,
                     8.385632, -3.8731985, -0.77734005, 1.1250188, 5.5334535, 1.3838477, 2.928386, -7.117574, 4.660319,
                     4.122918, 6.2692857, 3.9600768, 3.6266282, -3.9231815, -11.483488, -1.4674958, 0.76077706,
                     4.5815387, -5.360802, -3.9554005, 0.22725116, 0.0731676, -6.05242, 4.8052797, 4.3125854,
                     -4.4149523, -1.4391105, 7.449903, 0.954129, -2.6284962, -8.103558, -14.728931, 3.3570845,
                     -14.22315, 2.6697586, -0.20069852, -3.885065, -3.990585, 1.6972332, 9.658651, -4.690506, 4.3081613,
                     -10.211507, 2.507145, -4.110533, 4.3702216, -3.347643, 6.6676416, -7.448882, 4.4626317, -4.7397118,
                     3.5940218, -6.744161, 5.7114515, -4.3098187, 1.0758209, -6.7034473, 0.6825727, -1.7641339,
                     -6.04819, 0.5866624, -6.718653, -3.8531768, 2.1197135, 4.546326, -4.0387177, 10.267389, 9.128508,
                     -0.62199795, -5.954187, -4.508144, 0.4189416, -2.2084744, -7.381515, -3.836414, -1.0863944,
                     3.1144316, -2.1529253, -8.33139, 9.003711, -6.2985682, -1.4480758, -2.4382284, 0.62422013,
                     -7.0803494, 11.220451, 1.2706772, 4.061172, -0.5172092, -1.7305009, 0.6920172, -11.063449,
                     3.8686216, 0.084270544, -8.532835, 2.1548378, -6.424178, 6.1432595, -2.837454, -1.7763672,
                     2.4377222, -2.2671163, -1.6683736, -2.5935316, 4.123942, -7.302589, -6.0431123, -4.012489,
                     -2.19556, 2.7243242, 2.9890049, 6.1929107, -0.16905196, 0.5284386, -1.4016376, 4.5065703, 7.935183,
                     3.2161472, 7.5298386, 0.8870081, 7.453709, 5.1509748, -13.555357, -7.674622, 6.196169, -1.8152577,
                     -3.6804855, -2.8483763, 4.5060725, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    # Start search
    print(len(query_vectors))
    res = client.search(
        collection_name=collection_name,  # target collection
        data=query_vectors,  # query vectors
        limit=limit,  # number of returned entities
    )

    # Process search results
    results = []
    origin_files = set()

    for entity in res:
        print(entity)
        vector_id = entity[0]  # Accessing the first element of the list
        cosine_similarity_value = entity[1]

        # Append the tuple (vector_id, cell_name, file_name, cosine_similarity_value) to the results list
        results.append((vector_id, cosine_similarity_value))
        # origin_files.add(file_name)

    # Sort results by cosine similarity value (descending order)
    results.sort(key=lambda x: x[1], reverse=True)

    # Create a dictionary with keys "file_name" and "results"
    output = {"filenames": origin_files, "results": results}

    # Print the dictionary
    print(output)
