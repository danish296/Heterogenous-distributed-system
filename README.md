# 🚀 Heterogeneous Distributed Task Processor

A cloud-native application demonstrating a real-world, distributed, and heterogeneous microservices architecture. This project offloads computationally intensive tasks from a master node to specialized worker nodes running on separate cloud servers.

## 🏛️ Project Architecture

This project is built on a Master-Worker distributed computing model. The "Master" (or Coordinator) is a user-facing application that delegates tasks to a fleet of specialized "Worker" systems. For this deployment, the Master runs on a local machine, and the Workers run on separate, independent AWS EC2 cloud servers.

```
+--------------------------+
|      User's Browser      |
+--------------------------+
            |
            v
+--------------------------+
|  Your Local PC (Master)  |
| (Running Streamlit App)  |
+--------------------------+
            |
            v (Internet - HTTP Requests)
+-------------------------------------------------------------+
|                                                             |
|   +-----------------------+   +--------------------------+  |
|   |  AWS EC2 Server 1     |   |   AWS EC2 Server 2       |  |
|   | (Python Grayscale     |   |  (Node.js Sepia Worker)  |  |
|   |       Worker)         |   |                          |  |
|   | IP: 15.206.69.89:5001 |   |  IP: 13.126.20.248:5002  |  |
|   +-----------------------+   +--------------------------+  |
|                                                             |
|                   AWS Cloud Infrastructure                  |
+-------------------------------------------------------------+
```

## 🛠️ Tech Stack

| Master / Coordinator | Worker 1 (Grayscale) | Worker 2 (Sepia) | Infrastructure & Deployment |
|:-------------------:|:--------------------:|:-----------------:|:---------------------------:|
| Python & Streamlit | Python & Flask | Node.js & Express | AWS, Docker, GitHub |

## 📋 Workflow

1. **User Interaction**: The user accesses the Streamlit web application running on the local Master PC and uploads an image.

2. **Task Delegation**: The Master application splits the image into two horizontal strips.

3. **Distributed Processing**:
   - The Master sends the top strip via an HTTP POST request over the internet to the Python Worker running on an AWS server.
   - Simultaneously, it sends the bottom strip to the Node.js Worker on a separate AWS server.

4. **Independent Execution**:
   - The Python worker receives its image strip, uses the Pillow library to convert it to grayscale, and sends the processed image data back in the HTTP response.
   - The Node.js worker receives its strip, uses the Jimp library to apply a sepia filter, and sends its processed image data back.

5. **Result Aggregation**: The Master application receives the two processed image strips from the workers.

6. **Final Output**: The Master stitches the two strips back together into a single image and displays the final result to the user in the web browser.

## 🚀 Setup and Execution

Follow these steps to deploy and run the entire distributed system.

### Part 1: Deploying the Workers on AWS

#### Prerequisites
- An AWS account with Free Tier access
- This project cloned and pushed to your own GitHub repository

#### Launch EC2 Instances

1. Log in to the AWS EC2 Dashboard and launch two `t2.micro` instances using the Ubuntu OS Image (AMI).

2. Create a new key pair (e.g., `my-key.pem`) and save it securely.

3. Create a new security group (firewall) and add the following inbound rules:

   | Type       | Port Range | Source    |
   |------------|------------|-----------|
   | SSH        | 22         | My IP     |
   | Custom TCP | 5001       | 0.0.0.0/0 |
   | Custom TCP | 5002       | 0.0.0.0/0 |

4. Launch both instances using the same key pair and security group.

#### Deploy Code to Each Server

Find the Public IPv4 address for each of your EC2 instances.

**For the Python Worker:**

1. SSH into the server:
   ```bash
   ssh -i "path/to/my-key.pem" ubuntu@<PYTHON_WORKER_IP>
   ```

2. Run the setup commands:
   ```bash
   sudo apt update
   sudo apt install git python3-pip python3-venv libjpeg-dev zlib1g-dev -y
   git clone <your_github_repo_url>
   cd your-repository-name/worker-python
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   nohup python3 app.py &
   ```

**For the Node.js Worker:**

1. Open a new terminal and SSH into the second server:
   ```bash
   ssh -i "path/to/my-key.pem" ubuntu@<NODEJS_WORKER_IP>
   ```

2. Run the setup commands:
   ```bash
   sudo apt update
   sudo apt install git nodejs npm -y
   git clone <your_github_repo_url>
   cd your-repository-name/worker-nodejs
   npm install
   nohup node server.js &
   ```

### Part 2: Running the Master Application Locally

#### Configure IP Addresses
1. On your local computer, open the `coordinator/app.py` file.
2. Update the `WORKER_URLS` list with the public IPs of your AWS servers.

#### Run the App

1. Open a terminal on your local PC and navigate to the coordinator folder.

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows:
   .\venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies and run the application:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

4. Your web browser will open with the application ready to use.

## 🐛 Troubleshooting Common Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| Permission denied (publickey) | The .pem key file is not secured properly on your local machine | On Windows, go to File Properties > Security > Advanced, disable inheritance, and remove all users except your own |
| externally-managed-environment | Newer Ubuntu versions prevent pip from installing packages globally | Always create and activate a virtual environment (`python3 -m venv venv` and `source venv/bin/activate`) before running `pip install` |
| Connection Refused or Timeout in Streamlit App | The worker application is not running on the AWS server, or the AWS Security Group is blocking the port | SSH into the worker server and check `ps aux` or restart the worker process |
| Failed building wheel for Pillow | The AWS server is missing system-level libraries needed to compile the Python Pillow package | Install the required dependencies on the server before running pip install: `sudo apt install libjpeg-dev zlib1g-dev -y` |

## 💡 Future Suggestions

- **Implement a Load Balancer**: Add a service like Nginx to sit in front of the workers. This would allow you to scale the number of workers dynamically without changing the master's configuration.

- **Containerize the Deployment**: Use the existing Dockerfiles to deploy the workers as containers to a service like AWS Elastic Container Service (ECS) or Google Cloud Run for easier management and auto-scaling.

- **Add More Workers**: Create new workers for different tasks (e.g., video processing, text analysis) to make the system even more powerful and heterogeneous.

## 📁 Project Structure

```
heterogeneous-distributed-task-processor/
├── coordinator/
│   ├── app.py
│   └── requirements.txt
├── worker-python/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── worker-nodejs/
│   ├── server.js
│   ├── package.json
│   └── Dockerfile
└── README.md
```

## 🚀 Technologies Used

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)
![AWS](https://img.shields.io/badge/Amazon_AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

---

**Created by Danish Akhtar**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/danish296)
