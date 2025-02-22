# airflow-pgsql-container-setup-for-triggering-emr-job

1. Docker & Docker Compose Installation on the ec2 instance.
2. Airflow directory and its related folder creation.
   **mkdir airflow && cd airflow**
   **vi docker-compose.yml**
   **mkdir -p ./dags ./logs ./plugins ./scripts**
   **sudo chmod -R 777 ./logs ./dags ./plugins ./scripts**
   **sudo docker compose up -d / sudo docker compose down**
   **docker exec -it airflow /bin/bash**
   **docker exec -it postgres psql -U airflow -d airflowDB**
   **airflow users create --username rasans --password rasans@12345 --firstname sram --lastname lnu --role User --email alan@example.com --verbose**
   **sudo docker logs airflow**
3. Whitelist port 5432 & 8080 in the vpc security of the ec2 instance.














