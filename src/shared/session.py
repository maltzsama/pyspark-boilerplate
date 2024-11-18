import os

# pylint:disable=E0401
try:
    import pyspark
except:
    import findspark

    findspark.init()
    import pyspark


def create_session(app_name: str, run_locally: bool = True) -> object:
    """
    Creates a Spark Session.

    Args:
    - app_name (str): Application name.
    - run_locally (bool): Indicates whether the execution is local or not. Default: True.

    Returns:
    - spark (object): Spark Session.
    """

    if 'GLUE_EZE' in os.environ:
        run_locally = False

    try:
        if run_locally:
            import find_spark
            spark = find_spark.get_spark_session(app_name)
        else:
            from pyspark.sql import SparkSession
            spark = SparkSession.builder.appName(app_name).config("spark.security.manager.enabled", "false").getOrCreate()
    except ImportError:
        # If find_spark is not found, use pyspark
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.appName(app_name).config("spark.security.manager.enabled", "false").getOrCreate()

    return spark