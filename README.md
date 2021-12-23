# Spark-Streaming-Kafka

Demo for storing Kafka Messages as Parquet in HDFS using Spark Streaming.

## Instructions

First you need to create the Python dependencies package. To do that, run:

```bash
pip install -t dependencies-pkg -r requirements.txt
zip -r dependencies-pkg.zip ./dependencies-pkg
rm -rf dependencies-pkg;
```

Then modify the config.yaml file according to below and submit the Spark job!

### Debugging

For printing the events in the console, set the config file as:

```yaml
AppName: YOUR-APP-NAME
MasterMode: "local[*]"

Stream:
  Read:
    TopicName: YOUR-KAFKA-TOPIC-NAME
    StartingOffsets: earliest
  Write:
    Format: console
    OutputMode: append
    TriggerTime: "30 seconds"
```

and submit with:

```bash
spark-submit \
--master local \
--deploy-mode client \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 \
--files config.yaml \
--py-files dependencies-pkg.zip \
stream.py
```

### Cluster with YARN and HDFS

For processing the events and outputting them as a Parquet file, set the config files as:

```yaml
AppName: YOUR-APP-NAME
MasterMode: yarn

Stream:
  Read:
    BootstrapServers:
      - "HOST1:PORT1"
      - "HOST2:PORT2"
    TopicName: YOUR-KAFKA-TOPIC-NAME
    StartingOffsets: earliest
  Write:
    Format: parquet
    OutputMode: append
    OutputPath: YOUR OUTPUT PATH
    TriggerTime: "30 seconds"
    CheckpointPath: YOUR-CHECKPOINT-PATH
```

and submit with:

```bash
spark-submit \
--master yarn \
--deploy-mode cluster \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 \
--files config.yaml \
--py-files dependencies-pkg.zip \
stream.py
```

