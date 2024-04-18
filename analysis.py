import os

import pandas as pd
# import scanpy as sc
from matplotlib.pyplot import rc_context


# Todo: Jason: Implement this
def get_similar_genes(similarity_obj, top_n=10):
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
    cell_genes = {}
    for file in similarity_obj[1]:
        filepath = os.path.join('data', file)
        cell_genes[file] = pd.read_csv(filepath, delimiter=',', nrows=0)
    for query_vec in similarity_obj[0].keys():
        for match in similarity_obj[0][query_vec]:
            print(f'file: {match}')
            cell_id = match[0] - 100000

            filepath = os.path.join('data', match[2])

            data = pd.read_csv(filepath, delimiter=',', nrows=1, skiprows=cell_id+1, header=None)
            data_list = data.loc[:, :].values.flatten().tolist()
            cell_genes[match[2]].loc[len(cell_genes[match[2]])] = data_list


    # Find the top_n most expressed genes
    # Code from: https://stackoverflow.com/questions/34518634/finding-highest-values-in-each-row-in-a-data-frame-for-python
    # expressed_genes = pd.DataFrame({n: df.T[col].nlargest(top_n).index.tolist() for n, col in enumerate(df.T)}).T
    # index = 0
    # offset = len(similarity_obj[0].keys())
    top_n_cell_genes = {}
    for file in cell_genes.keys():
        data = cell_genes[file]
        cell_ids = data[['Unnamed: 0']].copy()
        cell_ids.rename(columns={'Unnamed: 0': -1}, inplace=True)
        data = data.drop(columns=['Unnamed: 0'], axis=1)
        expressed_genes = pd.DataFrame({n: data.T[col].nlargest(top_n).index.tolist() for n, col in enumerate(data.T)}).T

        # Join back in cell_ids
        expressed_genes = expressed_genes.join(cell_ids)

        # Put cell_id column first
        expressed_genes = expressed_genes.reindex(columns=sorted(expressed_genes.columns))
        expressed_genes.rename(columns={-1: 'cell_ids'}, inplace=True)
        top_n_cell_genes[file] = expressed_genes




    for file in top_n_cell_genes.keys():
        save_path = os.path.join('data', f'{file}_top{top_n}_to_id_100000.csv')
        top_n_cell_genes[file].to_csv(save_path, index=False)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 300)
    #print(f'cell_genes: {cell_genes}')
    print(f'expressed genes: {top_n_cell_genes}')



def plot_umap(gene_map):
    """
    Make a umap plot. Save plot to figures/
    :param gene_map:
    :return:
    """

    # https://scanpy.readthedocs.io/en/stable/generated/scanpy.tl.umap.html
    # https://scanpy.readthedocs.io/en/stable/tutorials/plotting/core.html

    pass
