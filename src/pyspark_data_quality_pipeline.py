"""PySpark Bronze-to-Silver pipeline suitable for Azure Databricks or local Spark."""
from pathlib import Path
from pyspark.sql import SparkSession, functions as F, Window

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "processed_spark"
spark = SparkSession.builder.appName("SyntheticFinancialHealthDQ").getOrCreate()

customers = spark.read.option("header", True).option("inferSchema", True).csv(str(RAW / "customers.csv"))
accounts = spark.read.option("header", True).option("inferSchema", True).csv(str(RAW / "accounts.csv"))
transactions = spark.read.option("header", True).option("inferSchema", True).csv(str(RAW / "transactions.csv"))
snapshots = spark.read.option("header", True).option("inferSchema", True).csv(str(RAW / "balance_snapshots.csv"))

valid_customers = customers.filter(F.col("customer_id").isNotNull() & (F.trim("customer_id") != ""))
clean_tx = (transactions.dropDuplicates(["transaction_id"])
            .withColumn("category", F.coalesce(F.nullif(F.trim("category"), F.lit("")), F.lit("Unclassified")))
            .withColumn("transaction_date", F.to_date("transaction_date")))

latest = (snapshots.withColumn("rn", F.row_number().over(Window.partitionBy("account_id").orderBy(F.col("snapshot_date").desc())))
          .filter("rn = 1").drop("rn"))
movement = clean_tx.groupBy("account_id").agg(F.sum("amount").alias("net_movement"))
recon = (accounts.join(movement, "account_id", "left").join(latest, "account_id")
         .withColumn("calculated_closing_balance", F.round(F.col("opening_balance") + F.coalesce("net_movement", F.lit(0)), 2))
         .withColumn("difference", F.round(F.col("calculated_closing_balance") - F.col("closing_balance"), 2))
         .withColumn("status", F.when(F.abs("difference") <= F.lit(.01), "PASS").otherwise("FAIL")))

for name, frame in {"dim_customer": valid_customers, "dim_account": accounts, "fact_transaction": clean_tx,
                    "fact_balance_snapshot": snapshots, "balance_reconciliation": recon}.items():
    frame.write.mode("overwrite").format("parquet").save(str(OUT / name))

assert valid_customers.count() == 1000
assert clean_tx.select("transaction_id").distinct().count() == clean_tx.count()
assert recon.filter("status = 'FAIL'").count() == 0
print("DQ pipeline passed; Silver parquet tables written to", OUT)
