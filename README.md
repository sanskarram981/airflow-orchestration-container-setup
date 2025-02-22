# airflow-pgsql-container-setup-for-triggering-emr-job

1. Docker & Docker Compose Installation on the ec2 instance.
2. Airflow directory and its related folder creation.<br>
   **mkdir airflow && cd airflow**<br>
   **vi docker-compose.yml**<br>
   **mkdir -p ./dags ./logs ./plugins ./scripts**<br>
   **sudo chmod -R 777 ./logs ./dags ./plugins ./scripts**<br>
   **sudo docker compose up -d / sudo docker compose down**<br>
   **docker exec -it airflow /bin/bash**<br>
   **docker exec -it postgres psql -U airflow -d airflowDB**<br>
   **airflow users create --username rasans --password rasans@12345 --firstname sram --lastname lnu --role User --email rasans@example.com --verbose**<br>
   **sudo docker logs airflow**<br>
3. Whitelist port 5432 & 8080 in the vpc security of the ec2 instance.














