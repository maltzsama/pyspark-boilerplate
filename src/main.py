#!/usr/bin/python
"""
Run a PySpark job with specified job module and arguments.

This script is designed to execute a specified PySpark job by dynamically importing
a module from the 'jobs' package. The user can specify the job name and any additional
arguments needed for the job.

Usage:
    python script_name.py --job <job_module_name> [--job-args <key=value> ...]

Args:
    --job (str): Required. The name of the job module to run (e.g., 'poc' runs 'jobs.poc').
    --job-args (list): Optional. Additional key=value arguments to pass to the job.

Environment:
    PYSPARK_JOB_ARGS: Set with provided --job-args to pass environment variables to PySpark.

Example:
    python script_name.py --job example_job --job-args template=manual-email foo=bar

Notes:
    - Checks if 'libs.zip' and 'jobs.zip' files exist to insert them into the sys.path.
    - Initializes Spark context and runs the specified job module with provided arguments.
    - Measures and prints the job execution time.

"""

import argparse
import importlib
import time
import os
import sys
import logging

from shared.session import create_session


# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if os.path.exists("libs.zip"):
    sys.path.insert(0, "libs.zip")
else:
    sys.path.insert(0, "./libs")

if os.path.exists("jobs.zip"):
    sys.path.insert(0, "jobs.zip")
else:
    sys.path.insert(0, "./jobs")



if __name__ == "__main__":
    start = time.time()

    parser = argparse.ArgumentParser(description="Run a PySpark job")
    parser.add_argument(
        "--job",
        type=str,
        required=True,
        dest="job_name",
        help="The name of the job module you want to run. (ex: poc will run job on jobs.poc package)",
    )
    parser.add_argument(
        "--job-args",
        nargs="*",
        help="Extra arguments to send to the PySpark job (word: --job-args template=manual-email1 foo=bar",
    )

    args = parser.parse_args()
    logger.info("Called with arguments: %s", args)

    environment = {"PYSPARK_JOB_ARGS": " ".join(args.job_args) if args.job_args else ""}

    job_args = dict()
    if args.job_args:
        job_args_tuples = [arg_str.split("=") for arg_str in args.job_args]
        logger.info("job_args_tuples: %s", job_args_tuples)
        job_args = {a[0]: a[1] for a in job_args_tuples}

    logger.info("Running job %s...\nenvironment is %s\n", args.job_name, environment)

    os.environ.update(environment)

    try:
        spark_session = create_session(args.job_name)
        job_module = importlib.import_module(f"jobs.{args.job_name}.{args.job_name}")

        job_module.run(spark_session, logger)

    except Exception as e:
        logger.error(f"Job Execution error: {args.job_name}: {str(e)}")

    finally:
        end = time.time()
        logger.info("Execution of job %s took %s seconds", args.job_name, end - start)
