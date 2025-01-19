<h1>Weight Station Project</h1>

<p>This project is a weight station application that allows users to record and manage container weights. It provides a web interface for interacting with the system and stores the data in a MySQL database.</p>

<h2>Prerequisites</h2>
<p>Before running the application, make sure you have the following installed:</p>
<ul>
    <li>Python 3.x</li>
    <li>Docker</li>
    <li>Docker Compose</li>
    <li>jq (for JSON formatting)</li>
</ul>

<h2>Project Setup</h2>

<h3>1. Clone the repository:</h3>
<pre><code>git clone https://github.com/arielfe/DeveleapDevWeek.git
cd DeveleapDevWeek
git checkout Weight</code></pre>

<h3>2. Navigate to the project directory:</h3>
<pre><code>cd Weight</code></pre>

<h2>Database Setup</h2>
<p>You have two options to set up the database:</p>

<h3>Option 1: Using Docker Compose (Recommended)</h3>
<p>This method provides persistent data storage and easier management:</p>
<pre><code>docker-compose up --build</code></pre>
## Database Updates

To update the shared database data:
1. Export your current database:
   ```bash
   docker exec weight_mysql mysqldump -unati -pbashisthebest weight > weightdb.sql

<h3>Option 2: Manual Docker Setup</h3>
<p>If you prefer manual setup:</p>
<pre><code># Build the MySQL database Docker image
docker build -t weight-station-db .

# Run the MySQL database container
docker run -d \
  --name weight-station-mysql \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=root123 \
  weight-station-db</code></pre>

<h2>Running the Application</h2>

<h3>1. Create and activate virtual environment:</h3>
<pre><code>python3 -m venv myenv
source myenv/bin/activate</code></pre>

<h3>2. Install dependencies:</h3>
<pre><code>pip install -r requirements.txt</code></pre>

<h3>3. Run the application:</h3>
<pre><code>python app.py</code></pre>

<p>Access the application at <strong>http://localhost:5000</strong></p>

<h2>Database Operations</h2>
<p>Connect to the MySQL database using either method:</p>

<h3>Option 1: Connect as root:</h3>
<pre><code>docker exec -it weight_mysql mysql -uroot -proot123</code></pre>

<h3>Option 2: Connect as application user:</h3>
<pre><code>docker exec -it weight_mysql mysql -unati -pbashisthebest</code></pre>

<h3>Common Database Commands:</h3>
<pre><code># List databases
SHOW DATABASES;

# Use weight database
USE weight;

# List tables
SHOW TABLES;

# View transactions
SELECT * FROM transactions;

# View registered containers
SELECT * FROM containers_registered;</code></pre>

<h2>API Endpoints</h2>
<p>Test the API endpoints using curl:</p>

<h3>1. GET weight records (with formatted JSON output):</h3>
<pre><code>curl "http://localhost:5000/weight?t1=20240101000000&t2=20240119235959" | jq '.'</code></pre>

<h3>2. POST new weight:</h3>
<pre><code>curl -X POST "http://localhost:5000/weight" \
-H "Content-Type: application/json" \
-d '{
    "direction": "in",
    "truck": "TRUCK123",
    "containers": "C1,C2",
    "weight": 1000,
    "unit": "kg"
}'</code></pre>

<h2>Data Persistence</h2>
<p>When using docker-compose, data persists between container restarts. To start fresh:</p>
<pre><code># Remove containers and volumes
docker-compose down -v

# Rebuild and start
docker-compose up --build</code></pre>

<h2>Troubleshooting</h2>
<ul>
    <li>If you see connection errors, ensure the MySQL container is running:
        <pre><code>docker ps | grep mysql</code></pre>
    </li>
    <li>To view MySQL logs:
        <pre><code>docker-compose logs mysql</code></pre>
    </li>
    <li>To install jq for JSON formatting:
        <pre><code># Ubuntu/Debian
sudo apt-get install jq

# MacOS
brew install jq</code></pre>
    </li>
</ul>
