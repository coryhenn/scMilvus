from pymilvus import MilvusClient

# Define your Milvus connection parameters
CLUSTER_ENDPOINT = "http://localhost:19530"
TOKEN = "YOUR_CLUSTER_TOKEN"  # If required

# Set up a Milvus client
client = MilvusClient(
    uri=CLUSTER_ENDPOINT,
    token=TOKEN
)

# List all collections
collections = client.list_collections()

# Print the list of collections
print("Collections in the database:")
for collection in collections:
    print(collection)  # Print the collection object itself

# Drop the collection
# client.drop_collection("PoolAscRNAseq")
