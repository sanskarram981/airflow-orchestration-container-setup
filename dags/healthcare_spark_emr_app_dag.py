from datetime import datetime
from airflow import DAG
from airflow.providers.amazon.aws.operators.emr import EmrCreateJobFlowOperator, EmrTerminateJobFlowOperator,EmrAddStepsOperator
from airflow.providers.amazon.aws.sensors.emr import EmrJobFlowSensor,EmrStepSensor


default_args = {
    'owner': 'rasans',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 17)
}

JOB_FLOW_OVERRIDES = {
    "Name": "HealthCareApp-EMR-Cluster",
    "ReleaseLabel": "emr-6.15.0",
    "Applications": [{"Name": "Spark"}, {"Name": "Hadoop"},{"Name": "Hive"}],
    "Instances": {
        "InstanceGroups": [
            {
                "Name": "Master nodes",
                "Market": "ON_DEMAND",
                "InstanceRole": "MASTER",
                "InstanceType": "m5.xlarge",
                "InstanceCount": 1,
            },
            {
                "Name": "Core nodes",
                "Market": "ON_DEMAND",
                "InstanceRole": "CORE",
                "InstanceType": "m5.xlarge",
                "InstanceCount": 2,
            }
        ],
        "KeepJobFlowAliveWhenNoSteps": True,
        "TerminationProtected": False,
    },
    "BootstrapActions": [],
    "Configurations": [],
    "JobFlowRole": "EMR_EC2_DefaultRole",
    "ServiceRole": "EMR_DefaultRole",
    "LogUri": "s3a://heathcare-emr-rasans-bucket/emr-logs/",
}

SPARK_STEPS = [
    {
        "Name": "Step 1 - Run Spark Job 1",
        "ActionOnFailure": "CONTINUE",
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": [
                "spark-submit",
                "--deploy-mode", "cluster",
                "--class", "org.apache.spark.examples.SparkPi",
                "s3://your-bucket/spark-jobs/spark-job-1.jar",
                "10"
            ],
        },
    },
    {
        "Name": "Step 2 - Run Spark Job 2",
        "ActionOnFailure": "CONTINUE",
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": [
                "spark-submit",
                "--deploy-mode", "cluster",
                "--class", "org.apache.spark.examples.WordCount",
                "s3://your-bucket/spark-jobs/spark-job-2.jar",
                "s3://your-input-bucket/",
                "s3://your-output-bucket/"
            ],
        },
    },
]



with DAG(
        dag_id="create_emr_cluster_and_run_spark_job",
        default_args=default_args,
        schedule_interval=None,
        catchup=False) as dag:

    create_emr_cluster = EmrCreateJobFlowOperator(
        task_id="create_emr_cluster",
        job_flow_overrides=JOB_FLOW_OVERRIDES,
        aws_conn_id="aws_default")

    wait_for_emr_cluster = EmrJobFlowSensor(
        task_id="wait_for_emr_cluster",
        job_flow_id="{{ ti.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
        target_states=["WAITING"],
        poke_interval=30,
        timeout=900
    )

    add_spark_steps = EmrAddStepsOperator(
        task_id="add_spark_steps",
        job_flow_id="{{ ti.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
        steps=SPARK_STEPS,
    )

    wait_for_step_1_completion = EmrStepSensor(
        task_id="wait_for_step_1",
        job_flow_id="{{ ti.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        step_id="{{ ti.xcom_pull(task_ids='add_spark_steps', key='return_value')[0] }}",
        aws_conn_id="aws_default",
    )

    # Task 5: Wait for Step 2 Completion
    wait_for_step_2_completion = EmrStepSensor(
        task_id="wait_for_step_2",
        job_flow_id="{{ ti.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        step_id="{{ ti.xcom_pull(task_ids='add_spark_steps', key='return_value')[1] }}",
        aws_conn_id="aws_default",
    )


    terminate_emr_cluster = EmrTerminateJobFlowOperator(
        task_id="terminate_emr_cluster",
        job_flow_id="{{ ti.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
        trigger_rule="all_done"
    )

    create_emr_cluster >> wait_for_emr_cluster >> add_spark_steps >> [wait_for_step_1_completion,wait_for_step_2_completion] >> terminate_emr_cluster
