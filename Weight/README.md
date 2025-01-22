<h1>Weight Station Project</h1>

<p>This project is a weight station application that allows users to record and manage container weights. It provides a web interface for interacting with the system and stores the data in a MySQL database.</p>

<h2>Prerequisites</h2>
<p>Before running the application, make sure you have the following installed:</p>
<ul>
    <li>Docker</li>
    <li>Docker Compose</li>
    <li>jq (for JSON formatting)</li>
</ul>

<h2>Project Setup</h2>

<h3>1. Clone the repository:</h3>
<pre><code>git clone https://github.com/arielfe/DeveleapDevWeek.git
cd DeveleapDevWeek
git checkout Weight
cd Weight</code></pre>

<h2>Running the Application</h2>

<h3>First Time Setup / Reset Environment</h3>
<pre><code># Stop all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Remove all images related to this project
docker rmi weight_mysql weight_flask_app

# Rebuild and start
docker-compose up --build</code></pre>

<h3>Regular Usage</h3>
<pre><code># Start the application
docker-compose up

# Run in detached mode (background)
docker-compose up -d

# Stop the application
docker-compose down</code></pre>

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

<h3>3. Get /unknown containers:</h3>
<pre><code> curl "http://localhost:5000/unknown" | jq '.'</code></pre>
<h2>Data Persistence</h2>
<p>The data will persist between restarts unless you explicitly remove the volume:</p>
<pre><code># Remove the volume and start fresh:
docker-compose down -v

# Start services:
docker-compose up --build</code></pre>


<h2>Database Updates</h2>
<p>To update the shared database data:</p>
<ol>
    <li>Export your current database:
        <pre><code>docker exec weight_mysql mysqldump -unati -pbashisthebest weight > weightdb.sql</code></pre>
    </li>
    <li>Commit and push the changes:
        <pre><code>git add weightdb.sql
git commit -m "update: refresh database sample data"
git push origin Weight</code></pre>
    </li>
</ol>

<p>Team members can get the latest database by pulling and rebuilding:</p>
<pre><code>git pull
docker-compose down -v
docker-compose up --build</code></pre>

<h2>Troubleshooting</h2>
<ul>
    <li>If you see connection errors, ensure the MySQL container is running:
        <pre><code>docker ps | grep mysql</code></pre>
    </li>
    <li>To view MySQL logs:
        <pre><code>docker-compose logs mysql</code></pre>
    </li>
    <li>To view Flask application logs:
        <pre><code>docker-compose logs flask_app</code></pre>
    </li>
    <li>To install jq for JSON formatting:
        <pre><code># Ubuntu/Debian
<<<<<<< HEAD
sudo apt-get install jq</code></pre>
    </li>
</ul>

<h2>API Access</h2>
<p>Once running, the services will be available at:</p>
<ul>
    <li>Flask API: <code>http://localhost:5000</code></li>
    <li>Health Check: <code>http://localhost:5000/health</code></li>
    <li>MySQL Database: <code>localhost:3306</code></li>
</ul>
