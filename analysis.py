import os

import numpy as np
import pandas as pd
# import scanpy as sc
from matplotlib.pyplot import rc_context

def get_similar_cell_ids(similarity_obj):

    for query_vec in similarity_obj.keys():
        print(query_vec)
        cell_ids = pd.DataFrame(columns=[f'Cell_ids_query_{query_vec}'])
        for match in similarity_obj[query_vec]:

            cell_id = match[0]
            cell_ids.loc[len(cell_ids)] = cell_id

        save_path = os.path.join('data', f'ex_2_Pool_B_query{query_vec}.csv')
        cell_ids.to_csv(save_path, index=False)


def get_similar_genes(similarity_obj, file, top_n=327):
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

    # data = pd.read_csv('data/ex_1_pool_a.csv', delimiter=',', nrows=5, skiprows=2, header=None)
    #
    # print(data)


    # Get original gene data
    filepath = os.path.join('data', file)
    print(f'Loading data from {filepath}... ', end='')
    raw_data = pd.read_csv(filepath, delimiter=',')
    print('Done')

    cell_genes = pd.DataFrame(columns=np.arange(len(raw_data.columns)))
    for query_vec in similarity_obj[0].keys():
        counter = 0
        for match in similarity_obj[0][query_vec]:

            cell_id = match[0]
            print(f'file {counter} (id {cell_id}): {match}')

            #filepath = os.path.join('data', match[2])

            #data = pd.read_csv(filepath, delimiter=',', nrows=1, skiprows=cell_id-724, header=None)
            data = raw_data.loc[raw_data['Unnamed: 0'] == cell_id]
            data_list = data.loc[:, :].values.flatten().tolist()
            cell_genes.loc[len(cell_genes)] = data_list

            counter += 1

    print(cell_genes.head(10))

    # Find the top_n most expressed genes
    # Code from: https://stackoverflow.com/questions/34518634/finding-highest-values-in-each-row-in-a-data-frame-for-python
    # expressed_genes = pd.DataFrame({n: df.T[col].nlargest(top_n).index.tolist() for n, col in enumerate(df.T)}).T
    # index = 0
    # offset = len(similarity_obj[0].keys())
    data = cell_genes
    cell_ids = data[[0]].copy()
    save_path = os.path.join('data', f'{file}_top{top_n}_to_id_825_CELL_IDS.csv')
    cell_ids.to_csv(save_path, index=False)
    return
    cell_ids.rename(columns={0: -1}, inplace=True)
    data = data.drop(columns=[0], axis=1)
    expressed_genes = pd.DataFrame({n: data.T[col].nlargest(top_n).index.tolist() for n, col in enumerate(data.T)}).T

    # Join back in cell_ids
    expressed_genes = expressed_genes.join(cell_ids)

    # Put cell_id column first
    expressed_genes = expressed_genes.reindex(columns=sorted(expressed_genes.columns))
    expressed_genes.rename(columns={-1: 'cell_ids'}, inplace=True)

    save_path = os.path.join('data', f'{file}_top{top_n}_to_id_825.csv')
    expressed_genes.to_csv(save_path, index=False)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 300)
    #print(f'cell_genes: {cell_genes}')
    print(f'expressed genes: {expressed_genes}')



def plot_umap(gene_map):
    """
    Make a umap plot. Save plot to figures/
    :param gene_map:
    :return:
    """

    # https://scanpy.readthedocs.io/en/stable/generated/scanpy.tl.umap.html
    # https://scanpy.readthedocs.io/en/stable/tutorials/plotting/core.html

    pass
