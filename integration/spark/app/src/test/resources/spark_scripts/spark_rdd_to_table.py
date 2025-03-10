# Copyright 2018-2023 contributors to the OpenLineage project
# SPDX-License-Identifier: Apache-2.0

import random
import shutil
import string

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

spark = SparkSession.builder.master("local").appName("Spark rdd to table").getOrCreate()
spark.sparkContext.setLogLevel("info")

letters = string.ascii_lowercase


def rand_word():
    return "".join(random.choice(letters) for i in range(random.randint(4, 10)))


def tuple_to_csv(x):
    return ",".join([str(i) for i in x])


list_of_things = [(rand_word() + " " + rand_word(), random.randint(1, 100)) for i in range(100)]
rdd = spark.sparkContext.parallelize(list_of_things)
rdd.setName("list of random words and numbers")
csvDir = "/tmp/test_data/rdd_to_csv_output/"
try:
    shutil.rmtree(csvDir)
except OSError:
    print("output directory does not exist")

rdd.map(tuple_to_csv).saveAsTextFile(csvDir)

schema = StructType([StructField("name", StringType(), False), StructField("age", IntegerType(), False)])
spark.read.option("header", False).schema(schema).csv(csvDir).registerTempTable("test_people")

spark.sql("SELECT * FROM test_people WHERE age > 20 AND age < 65").write.mode("overwrite").option(
    "compression", "none"
).parquet("/tmp/test_data/rdd_to_table/")
