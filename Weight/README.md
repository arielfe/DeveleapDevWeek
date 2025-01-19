Weight Station Project
This project is a weight station application that allows users to record and manage container weights. It provides a web interface for interacting with the system and stores the data in a MySQL database.
Prerequisites
Before running the application, make sure you have the following installed:

Python 3.x
Docker

Project Setup

1. Clone the repository:
git clone https://github.com/arielfe/DeveleapDevWeek.git
cd DeveleapDevWeek
git checkout Weight

2. Navigate to the project directory:
cd Weight

3. Create a virtual environment:
python3 -m venv myenv

4. Activate the virtual environment:
source myenv/bin/activate

5. Install the project dependencies:
pip install -r requirements.txt


Database Setup

1. Build the MySQL database Docker image:
docker build -t weight-station-db .

2. Run the MySQL database container:
docker run -d \
  --name weight-station-mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=root123 \
  weight-station-db


Running the Application

1. Make sure the virtual environment is activated:
source myenv/bin/activate

2. Run the application:
python app.py

Access the application in your web browser at http://localhost:5000.

Database Operations
You can connect to the MySQL database and perform various operations:

1. Connect to the MySQL database:

- From the host machine:
docker exec -it weight-station-mysql mysql -uroot -proot123

- Or connect with the user 'nati' (from your code):
docker exec -it weight-station-mysql mysql -unati -pbashisthebest



2. Check Database Content: Once connected, you can:

- List databases:
SHOW DATABASES;

- Use the weight database:
USE weight;

- List tables:
SHOW TABLES;

- View transactions:
SELECT * FROM transactions;

- View registered containers:
SELECT * FROM containers_registered;




API Endpoints
You can test the API endpoints using tools like curl or Postman:

1. GET weight records:
curl "http://localhost:5000/weight?t1=20240101000000&t2=20240119235959"

2. POST new weight:
curl -X POST "http://localhost:5000/weight" \
-H "Content-Type: application/json" \
-d '{
    "direction": "in",
    "truck": "TRUCK123",
    "containers": "C1,C2",
    "weight": 1000,
    "unit": "kg"
}'