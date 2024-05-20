# scMilvus
Milvus implementation for scRNA-seq data

# Purpose
Here, we implement the vector database Milvus as a means for storing and retreiving single cell RNA sequencing (scRNAseq) data. scRNAseq datasets are large and complex. They require specialized processing to extract gene expression information and patterns from individual cells to understand cell states and lineages. In standard scRNAseq analysis, distance metrics, such as Euclidean and cosine similarity are used to cluster like cell types. From these clusters, gene expression, compared against reference datasets, allow for probabilistic identification of cell types. 

Vector databases (VDBs) are specialized databases that utilize high-dimensional vectors as the primary data structure for storing information [1]. In VDBs, data points are represented as multidimensional vectors, where each dimension corresponds to a specific attribute or feature of the data. These vectors can contain various types of numerical data, including integers and floating-point numbers, depending on the nature of the data being stored. In contrast to traditional relational database models that search columns and rows, VDBs perform similarity searches on data points using distance metrics such as Euclidean distance, dot product, or cosine similarity [2].

Given the hyperdimensional nature of scRNA-seq data and the multidimensional capabilities of VDBs, marrying the two could prove to enhance scRNA-seq data storage, processing, and manipulation. By querying cell similarity straight from the VDB, multiple similar experiments could be queried for cell state similarity/cell type. This could open up possibilities for experimental archive that allows for fast approximation of cell populations across experiments and treatment groups.

[1] Yikun Han, Chunjiang Liu, and Pengfei Wang. A Comprehensive Survey on Vector Database:
Storage and Retrieval Technique, Challenge. Preprint. 2023. arXiv: 2310.11703 [cs.DB].

[12] Toni Taipalus. “Vector database management systems: Fundamental concepts, use-cases, and
current challenges”. In: Cognitive Systems Research 85 (June 2024), p. 101216. issn: 1389-0417.
doi: 10.1016/j.cogsys.2024.101216. url: http://dx.doi.org/10.1016/j.cogsys.2024.
101216.
