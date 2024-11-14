# Coding Platform

Welcome to the **Coding Platform**, a web application inspired by LeetCode! This platform allows users to solve coding problems, view submission history, and manage problem sets in a structured, user-friendly environment. With JWT-based authentication, Dockerized code execution, and a clean interface, this application is ideal for coding enthusiasts and educators alike.

---

## Features

### 🧑‍💻 **Solve Problems**
- Browse a list of coding problems.
- View problem details, including descriptions, input/output formats, and sample test cases.
- Submit your solution and view the results in real time.
- Access previous submissions with the ability to review the code and execution results.

### ➕ **Manage Problems**
- Add new problems with details like name, description, sample input/output, and constraints.
- Edit existing problems to update information or test cases.

### 🔐 **Authentication**
- Secure login and registration with JWT-based authentication.
- Protected content access only for authenticated users.

### 🐳 **Isolated Code Execution**
- Submissions are executed in an isolated Docker environment for security and consistency.

## Installation

### Prerequisites
Before setting up the platform, make sure you have the following installed:
- **Python 3.8+**
- **Docker**


---

### Steps to Set Up the Platform

1. **Clone this repository:**
   ```bash
   git clone https://github.com/git-khandelwal/coding-platform
   cd coding-platform

2. **Activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

4. **Run the flask server:**
   ```bash
   flask run


### Running Submissions

**Ensure Docker is running**  
   Make sure Docker is installed and the Docker service is up and running on your machine. You can check this by running:
   ```bash
   docker --version
