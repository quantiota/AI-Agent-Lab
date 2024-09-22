
## Interview

As this task is designed to assess your ability to work independently, it’s crucial that you avoid seeking external help. Instead, please refer to internal documentation and resources (e.g., Docker, QuestDB, Grafana, VSCode) to resolve any issues you might encounter during the setup process. Part of this internship will involve troubleshooting and problem-solving, so demonstrating your ability to consult relevant documentation will be an important part of the evaluation.


### Step1: Install and Run the Docker Stack on Your Local Machine

As part of the interview process, we would like you to set up and run the Docker stack on your local machine, which will serve as your development environment during the internship. This will help us assess your familiarity with Docker and your ability to work with containerized services, as well as ensure that you are ready to begin development work.

#### Instructions:
1. **Clone or download** the Docker stack repository 
 https://github.com/quantiota/AI-Agent-Lab/
2. **Install Docker and Docker Compose** on your local machine (if not already installed). Ensure you have the latest versions installed.
3. **Run the Docker stack** using the provided `docker-compose.yml` file.
4. Access the following services locally to ensure everything is working:
   - **localhost:8080** (Code Server for VSCode)
   - **localhost:9000** (QuestDB)
   - **localhost:3000** (Grafana)
5. **Test the AI-Agent Lab**:
   - Run the `data-stream-processing.py` file in the **/notebooks/market-data/Binance/ folder**.
   - Verify that the data stream is being processed and check the data in **QuestDB** (available on **localhost:9000**).
   - Check the **Grafana dashboard** (on **localhost:3000**) to ensure the data is being visualized properly.
6. **Verify that all services** are running and accessible through your browser. The entire setup and testing process should take about **10 minutes** if Docker and Docker Compose are properly installed.


#### What You Should Submit:
- **Confirmation** that you’ve successfully set up the Docker stack and run the AI-Agent Lab.
- **Three specific screenshots** showing that the services are running and that the data from the data stream is being processed correctly:
  1. **localhost:8080**: A screenshot of **Code Server (VSCode)** running on your local machine, showing the terminal and editor open with the **`data-stream-processing.py`** file in the **/notebooks/market-data/Binance/ folder**. Ensure that the terminal output shows that the data stream has started processing.
  2. **localhost:9000**: A screenshot of **QuestDB** showing the **processed data from the Binance data stream**. Ensure that the screenshot clearly shows the relevant data in QuestDB after running **`data-stream-processing.py`**.
  3. **localhost:3000**: A screenshot of **Grafana** visualizing the **processed data from the Binance data stream**. Ensure that the Grafana dashboard is showing the correct visualization of the processed data from **QuestDB**.

- **Ensure that the following is clear in each screenshot**:
   - For **localhost:8080**: The terminal and editor in **VSCode** with the **`data-stream-processing.py`** file running and processing data.
   - For **localhost:9000**: The processed data from the **Binance data stream** visible in **QuestDB**.
   - For **localhost:3000**: The correct visualized data from the **Binance data stream** on the **Grafana dashboard**.

- **Screenshots should be clear** and demonstrate that the **data from the Binance data stream** is being processed and displayed correctly in all services.




 #### Important Note:

As part of the first step of the interview process, we ask all applicants to complete the Docker stack setup task and provide the required screenshots as described. This step is essential to ensure that you are familiar with Docker and can set up the development environment required for this internship.

If you are unable to complete this task or run the Docker stack, we kindly ask you to **withdraw your application** to allow us to focus on candidates who are technically prepared for the role.

We appreciate your understanding and encourage you to apply for future opportunities once you have gained more experience in this area.


### Step 2: Knowledge Assessment on Live Data Streams and Machine Learning

#### Instructions:

Please answer the following questions to help us assess your knowledge and experience with **live data streams** and **machine learning** relevant to the AI Agent Lab project.

### 1. Live Data Streams Knowledge:
- Describe your experience working with **live data streams** (e.g., financial market data, stock prices, cryptocurrency). Have you worked with any real-time data sources before? If yes, please provide a brief overview of the project and the technologies you used.
- If you have not worked with live data streams before, how would you approach integrating them into the AI Agent Lab? What resources would you consult, and what do you think are the key challenges in handling live data streams?

### 2. Machine Learning and API Integration:
- Share your experience with integrating **machine learning models** to process real-time data (e.g., regression, time-series forecasting, classification). Can you describe a project where you implemented machine learning algorithms with real-time data?
- What steps do you usually take to ensure the accuracy, reliability, and performance of machine learning models when processing live data? Provide any examples or best practices you've used.

### 3. Technical Problem-Solving (optional):
- Given the nature of the AI Agent Lab project, how would you design the integration of **live data streams** and **machine learning models** to process market data in real-time? Describe the general flow of data and the machine learning model’s role in making predictions or analyzing trends.

---

Please submit your responses within 24 hours for review. This will help us further evaluate your knowledge and fit for the project.
