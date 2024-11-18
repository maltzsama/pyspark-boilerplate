from pyspark.sql import DataFrame


def run(spark_session, logger, args=None):
    """
    run example_job job.

    Args:
    - spark_session (SparkSession): Sessão Spark.
    - args (dict): Argumentos do job.

    Returns:
    - None
    """

    logger.info("start example_job job...")

    data = [
        ("João", 25, "Brazil"),
        ("Maria", 31, "Portugal"),
        ("Pedro", 42, "Spain"),
    ]
    columns = ["name", "age", "country"]
    df: DataFrame = spark_session.createDataFrame(data, schema=columns)

    df.show()

    df_filtered = df.filter(df["age"] > 30)

    df_filtered.show()

    logger.info("Job example_job done.")