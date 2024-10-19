# Uploads Folder - AI Agent Lab

## Purpose

The `uploads` folder is used to store files that are uploaded through the AI Agent Lab web interface. It acts as a dedicated location for managing the files uploaded by users, ensuring that they are securely saved within the application.

### Key Features:
1. **File Storage**:
   - Any file uploaded through the AI Agent Lab UI (e.g., `.csv`, `.sql`, `.pdf`, `.txt`) will be stored in this folder.
   
2. **File Types**:
   - The application only allows files with the following extensions to be uploaded:
     - `.csv` (Comma-separated values)
     - `.sql` (SQL scripts)
     - `.pdf` (PDF documents)
     - `.txt` (Text files)
  
3. **Server-Side Storage**:
   - This folder is mounted within the `aiagentui` Docker container at `/aiagentui/uploads`, which allows seamless interaction between the web app and the containerized environment.
   - The host machine also has access to the `uploads` directory, so files are stored persistently on both the host and the container.
   