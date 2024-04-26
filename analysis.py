import copy
import os

import numpy as np
import pandas as pd
# import scanpy as sc
from matplotlib.pyplot import rc_context
from database_connections import find_similarities


def find_clusters(collection, seed_ids, limit=1024, iterations=5):
    cutoff = limit * iterations
    it_temp = iterations
    results = {}
    next_queries = set(seed_ids)
    already_queried = set()
    size = 100
    queried_cells = 0
    while iterations > 0:
        print(f'iter: {iterations}')
        # print(f'already queried: {already_queried}')
        # print(f'next_queries: {next_queries}')
        length = len(next_queries)

        print(f'cells to query: {length}')
        exit_loop = False
        next_queries2 = set()
        counter = size
        while True:
            query_list = []
            for j in range(size):
                try:
                    query_list.append(next_queries.pop())
                except KeyError:
                    exit_loop = True
                    break

            #print(f'query list: {query_list}')
            if not len(query_list):
                break

            milvus = find_similarities(collection, query_list, limit)
            queried_cells += len(query_list)
            print(f'Queried {counter}...')
            counter += size

            #print(milvus)
            for cell_id in milvus.keys():
                #print(milvus[cell_id])
                for cell_id2, _ in milvus[cell_id]:
                    if cell_id2 in results.keys():
                        results[cell_id2] += 1
                    else:
                        results[cell_id2] = 1

                already_queried.add(cell_id)
                # print(f'\tAQ: {already_queried}')
                for id2, _ in milvus[cell_id]:
                    # id, similarity tuple
                    if id2 not in already_queried:
                        # print(f'\tAdding {id2} to query')
                        next_queries2.add(id2)

            if exit_loop:
                break

        next_queries = set(next_queries2)
        # print(f'Queries for next it: {next_queries}')

        # print(f'cells to query: {length}')

        iterations -= 1


    counter3 = 0
    for key in results.keys():
        counter3 += results[key]
    print(f'queried cells: {queried_cells}, result length: {len(results.keys())}, res total: {counter3}')
    print(results)
    # Only return cells that appear iterations-1 times
    out = pd.DataFrame(columns=['cell_id', 'count'])
    for cid in results.keys():
        if results[cid] >= cutoff:
            temp = (cid, results[cid])
            out.loc[len(out)] = temp
    save_path = os.path.join('data', f'ex_2_seed{seed_ids[0]}-list_i{it_temp}_l{limit}.csv')
    out.to_csv(save_path, index=False)

    return out

    # print(f'iteration: {iterations}')
    # print(f'res beginning: {results}')
    # if iterations > 0:
    #     milvus = find_similarities(collection, seed_ids, limit)
    #     print(f'milvus: {milvus}')
    #     for cell_id in milvus.keys():
    #         if cell_id in results.keys():
    #             results[cell_id] += 1
    #         else:
    #             results[cell_id] = 1
    #         already_queried.add(cell_id)
    #
    #         next_queries = []
    #         for id2, _ in milvus[cell_id]:
    #             # id, similarity tuple
    #             if id2 not in already_queried:
    #                 print(f'not queried: {id2}')
    #                 next_queries.append(id2)
    #
    #         print(f'next queries: {next_queries}')
    #         print(f'res before: {results}')
    #         results = find_clusters(collection, next_queries, results, already_queried, limit=limit, iterations=iterations-1)
    #         print(f'res after: {results}')
    # else:
    #     print(f'END RES: {results}')
    #     return copy.deepcopy(results)




def get_similar_cell_ids(similarity_obj):

    for query_vec in similarity_obj.keys():
        print(query_vec)
        cell_ids = pd.DataFrame(columns=[f'Cell_ids_query_{query_vec}', 'cosine_sim'])
        for match in similarity_obj[query_vec]:

            cell_id = match[0]
            cell_ids.loc[len(cell_ids)] = (cell_id, match[1])

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
