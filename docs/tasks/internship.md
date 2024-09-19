### Task: Install and Run the Docker Stack on Your Local Machine

As part of the interview process, we would like you to set up and run the Docker stack on your local machine, which will serve as your development environment during the internship. This will help us assess your familiarity with Docker and your ability to work with containerized services, as well as ensure that you are ready to begin development work.

#### Instructions:
1. **Clone or download** the Docker stack repository (provide the link to your Docker Compose files or relevant repo).
2. **Install Docker and Docker Compose** on your local machine (if not already installed). Ensure you have the latest versions installed.
3. **Run the Docker stack** using the provided `docker-compose.yml` file.
4. Access the following services locally to ensure everything is working:
   - **localhost:8080** (Code Server for VSCode)
   - **localhost:9000** (QuestDB)
   - **localhost:3000** (Grafana)
5. **Test the AI-Agent Lab**:
   - Run the `data-stream-processing.py` file in the **Binance folder**.
   - Verify that the data stream is being processed and check the data in **QuestDB** (available on **localhost:9000**).
   - Check the **Grafana dashboard** (on **localhost:3000**) to ensure the data is being visualized properly.
6. **Verify that all services** are running and accessible through your browser. The entire setup and testing process should take about **10 minutes** if Docker and Docker Compose are properly installed.
