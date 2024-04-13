import os

from pymilvus import MilvusClient
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from global_variables import TOKEN, CLUSTER_ENDPOINT


# Todo: Jason: Implement this
def get_similar_genes(similarity_obj, top_n=5):
    """
    This function will:
        1. Find the original gene data for each cell in the top-n
            similar cells.
        2. Map the cell_ids to a cell_name from the respective experiment.
        3. Return a dictionary with the keys [cell_id, cell_name, top_genes]
            where cell_id and cell_name are from the vectors in Milvus and
            top_genes is a list of the top_n genes expressed in each cell, ordered
            most to least expressed.
    :param top_n: Top genes to return
    :param similarity_obj: A similarity dictionary from the find_similarities function
    :return: See 2.
    """
    print(f'** get_similar_genes function **')

    # Assume one experiment (file) only for now
    if len(similarity_obj[1]) != 1:
        print(f'Error: Only one experiment currently supported.')

    raw_data = None
    filepath = None
    for file in similarity_obj[1]:
        filepath = os.path.join('data', file)

    if filepath is None:
        print(f'Error: Filepath {filepath} is not valid')
        return

    raw_data = pd.read_csv(filepath, delimiter=',')

    if raw_data is None:
        print(f'Error: Could not read file: {filepath}')


    print(raw_data.head(5))



def plot_umap(gene_map):
    """
    Make a umap plot. Save plot to figures/
    :param gene_map:
    :return:
    """

    pass
