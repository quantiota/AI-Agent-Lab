# **Internship Instructions: Forking the Project and Using AI Agent Lab**

1. **Fork the Project**  
   - Begin by forking the project repository to your own GitHub account.
   - Ensure you regularly sync your fork with the upstream repository to stay updated with the latest changes.

2. **Set Up the AI Agent Lab Devbox**  
   - Use the **AI Agent Lab** as your dedicated development environment (devbox). This is mandatory for all tasks.
   - The **AI Agent Lab** is already set up with Docker, QuestDB, Code Server, Grafana, and other essential tools. 
   - You will need to use this stack to develop, test, and debug.
   - You **only need to add the following new volume mapping** to the existing Docker configuration:
     - Map the `docker` folder on your local machine to `/home/coder/project/docker` inside the container.
   - Do **not modify** the existing mappings or configuration except for this new addition.
   - If you're only modifying certain containers and don’t need to rebuild the entire stack, you can target specific services: `docker-compose up -d --build <service-name>`. This can save time by only rebuilding the container you're actively working on.


   Mapping the docker folder within the code-server is a good idea for easily modifying the Docker setup. By having the docker folder accessible inside the code-server, you can quickly edit the configuration files (like docker-compose.yml, Dockerfile, etc.) directly from the development environment, without needing to switch to a different tool or manually sync changes.

3. **Perform Tasks on the Provided Dedicated Server**  
   - We will provide you with access to a **dedicated server** to perform all development tasks.
   - The dedicated server will ensure that your work environment is isolated and optimized for development.
   - You will receive login credentials and instructions for accessing the server.

4. **Documentation and Updates**  
   - Document any changes you make to the codebase in detail. This includes new features, bug fixes, or optimizations.
   - Keep track of your progress, and provide regular status updates to the team.

5. **Communicate Any Issues**  
   - If you encounter any issues with the setup or tasks, communicate them as soon as possible so they can be addressed.
