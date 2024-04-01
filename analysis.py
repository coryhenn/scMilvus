import os

from pymilvus import MilvusClient
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from global_variables import TOKEN, CLUSTER_ENDPOINT


# Todo: Cory
def get_similiar_genes(similarity_dict, top_n):
    """
    This function will:
        1. Find the original gene data for each cell in the top-n
            similar cells.
        2. Map the cell_ids to a cell_name from the respective experiment.
        3. Return a dictionary with the keys [cell_id, cell_name, top_genes]
            where cell_id and cell_name are from the vectors in Milvus and
            top_genes is a list of the top_n genes expressed in each cell, ordered
            most to least expressed.
    :param similarity_dict: A similarity dictionary from the find_similarities function
    :return: See 2.
    """
    pass
