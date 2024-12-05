# **DynamoDB-MINI**

A distributed key-value store inspired by Amazon DynamoDB. This project focuses on providing **scalability**, **fault tolerance**, **high availability**, and **eventual consistency** through techniques such as **consistent hashing**, **vector clocks**, and **quorum-based algorithms**.

## **Features**
- **Decentralized Architecture**: Peer-to-peer communication with no single point of failure.
- **Replication and Fault Tolerance**: Asynchronous replication across nodes to handle failures.
- **Dynamic Load Balancing**: Ensures even load distribution across nodes.
- **Scalability**: Easily handles increased nodes and data without significant overhead.
- **Eventual Consistency**: Guarantees data consistency across replicas over time.
  
## **Directory Structure**

```
dynamodbMINI/
├── README.md                 # Project documentation
├── requirements.txt          # Dependencies
├── src/                      # Source code
│   ├── code/                 # Worker node implementation
│   │   ├── worker.py         # Main worker logic
│   │   ├── visualization.py  # Visualize routing and data distribution
│   │   └── client.py            # Client logic
│   ├── consistent-hashing/   # Hash ring implementation
│   │   └── HashRing.py       # Consistent hashing logic
├── tests/                    # Test the system using CLI
│   └── test.py
│   └── spawn_worker.py
│   └── test_redis_python.py
│   └── network_partition.py
├── presentation-report/    
│   └── report.pdf
│   └── slides given as link in this readme

```

## **Setup**

### **Prerequisites**
- Python 3.8+
- Redis (Ensure a Redis server is running locally or accessible remotely)

### **Install Dependencies**
Install all required Python packages:
```bash
pip install -r requirements.txt
```

### **Configuration**
The system configuration can be altered from the `./code/server.py`. Adjust settings such as:
- Number of replicas (`N`)
- Quorum values for reads (`R`) and writes (`W`)
- Redis connection details

## **Running the Project**

Follow these steps to start the system:

### 1. **Test the System**  
Ensure everything is working before running tests:
```bash
python3 ./code/client.py
python3 ./code/server.py
python3 ./consistent-hashing/HashRing.py
```
- The above command will ensure that client, server & the hashring are operational before testing.

## **Testing the System with CLI in  `test.py`**

After setting up the system, use `test.py` for functional tests:
```bash
python3 ./test/spawn_server.py
python3 ./test/test.py
```

## **Report & Slides**

Refer to the `presentation-report/` folder for in-depth detailed report:
- **Report.pdf**: Contains the complete report of our project.
- **Presentation.pdf**: Use this link for the presentation for this project `https://www.canva.com/design/DAGXtGrmcog/OD99_PKxzS7jMRGwOtjvig/edit?utm_content=DAGXtGrmcog&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton`
---