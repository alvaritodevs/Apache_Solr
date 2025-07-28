from pyspark.sql import SparkSession
import requests
import json

# Start Spark session
spark = SparkSession.builder \
    .appName("ETL Categories to Solr") \
    .getOrCreate()

""" Extract """
df = spark.read.csv("data/categories.csv", header=True, inferSchema=True)

""" Transform """
df_clean = df.select("id", "category_name", "product_number") \
    .na.drop()

# Convert to JSON
json_list = df_clean.toJSON().collect()
docs = [json.loads(doc) for doc in json_list]

""" Load to Solr """
SOLR_URL = "http://localhost:8983/solr/apache/update?commit=true"

response = requests.post(
    SOLR_URL,
    headers={"Content-Type": "application/json"},
    data=json.dumps(docs)
)

print(f"✅ Status: {response.status_code}")
print(response.text)
