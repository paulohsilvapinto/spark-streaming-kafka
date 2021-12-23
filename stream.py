from pyspark.sql import SparkSession
import pyspark.sql.functions as SF
from pyspark.sql.types import StructType, StructField, StringType
import yaml

with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

spark = (
    SparkSession.builder.appName(config["AppName"])
    .master(config["MasterMode"])
    .getOrCreate()
)

read_config = config["Stream"]["Read"]
write_config = config["Stream"]["Write"]

df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", ",".join(read_config["BootstrapServers"]))
    .option("subscribe", read_config["TopicName"])
    .option("startingOffsets", read_config["StartingOffsets"])
    .load()
)

regular_columns = [col for col, dtype in df.dtypes if not dtype.startswith("binary")]
binary_columns = [
    f"CAST({col} AS STRING) AS {col}"
    for col in df.columns
    if col not in regular_columns
]

df = df.selectExpr(*regular_columns, *binary_columns)

data_schema = StructType(
    [
        StructField("name", StringType(), False),
        StructField("address", StringType(), False),
    ]
)

df = df.select(*df.columns, SF.from_json(SF.col("value"), data_schema).alias("data"))
df = df.drop("value")

df = df.select(*df.columns, "data.*")
df = df.drop("data")

if (output_mode := write_config["OutputMode"]) == "console":
    df.writeStream.format(write_config["Format"]).outputMode(
        write_config["OutputMode"]
    ).trigger(processingTime=write_config["TriggerTime"]).start().awaitTermination()
else:
    df.writeStream.format(write_config["Format"]).option(
        "path", write_config["OutputPath"]
    ).outputMode(write_config["OutputMode"]).trigger(
        processingTime=write_config["TriggerTime"]
    ).option(
        "checkpointLocation", write_config["CheckpointPath"]
    ).start().awaitTermination()
