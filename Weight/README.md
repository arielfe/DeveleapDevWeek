&lt;!DOCTYPE html&gt;
&lt;html lang="en"&gt;
&lt;body&gt;
&lt;h1&gt;Weight Station Project&lt;/h1&gt;

&lt;p&gt;A comprehensive web application for managing truck and container weight tracking, built with Flask and MySQL.&lt;/p&gt;

&lt;h2&gt;🛠 Project Overview&lt;/h2&gt;
&lt;ul&gt;
    &lt;li&gt;Track truck and container weights with precision&lt;/li&gt;
    &lt;li&gt;Manage complex weighing transactions&lt;/li&gt;
    &lt;li&gt;Support for multiple weight units (kg/lbs)&lt;/li&gt;
    &lt;li&gt;Containerized deployment using Docker&lt;/li&gt;
&lt;/ul&gt;

&lt;h2&gt;📋 Prerequisites&lt;/h2&gt;
&lt;ul&gt;
    &lt;li&gt;Docker (version 20.10 or higher)&lt;/li&gt;
    &lt;li&gt;Docker Compose (version 1.29 or higher)&lt;/li&gt;
    &lt;li&gt;Git&lt;/li&gt;
    &lt;li&gt;jq (optional, for JSON formatting)&lt;/li&gt;
&lt;/ul&gt;

&lt;h2&gt;🚀 Project Setup&lt;/h2&gt;

&lt;h3&gt;Clone the Repository&lt;/h3&gt;
&lt;pre&gt;&lt;code&gt;git clone git@github.com:arielfe/DeveleapDevWeek.git
cd DeveleapDevWeek
git checkout Weight
cd Weight&lt;/code&gt;&lt;/pre&gt;

&lt;h3&gt;First Time Setup / Reset Environment&lt;/h3&gt;
&lt;pre&gt;&lt;code&gt;# Stop all containers
docker-compose down

# Remove volumes
docker-compose down -v

# Remove project images
docker rmi weight_mysql weight_flask_app

# Rebuild and start
docker-compose up --build&lt;/code&gt;&lt;/pre&gt;

&lt;h3&gt;Regular Usage&lt;/h3&gt;
&lt;pre&gt;&lt;code&gt;# Start the application
docker-compose up

# Run in detached mode
docker-compose up -d

# Stop the application
docker-compose down&lt;/code&gt;&lt;/pre&gt;

&lt;h2&gt;🗃️ Database Operations&lt;/h2&gt;

&lt;h3&gt;Connect to MySQL&lt;/h3&gt;
&lt;pre&gt;&lt;code&gt;# As root
docker exec -it weight_mysql mysql -uroot -proot123

# As application user
docker exec -it weight_mysql mysql -unati -pbashisthebest&lt;/code&gt;&lt;/pre&gt;

&lt;h3&gt;Common Database Commands&lt;/h3&gt;
&lt;pre&gt;&lt;code&gt;# List databases
SHOW DATABASES;

# Use weight database
USE weight;

# List tables
SHOW TABLES;

# View transactions
SELECT * FROM transactions;

# View registered containers
SELECT * FROM containers_registered;&lt;/code&gt;&lt;/pre&gt;

&lt;h2&gt;🌐 API Endpoints&lt;/h2&gt;

&lt;h3&gt;1. GET Weight Records&lt;/h3&gt;
&lt;pre&gt;&lt;code&gt;curl "http://localhost:5000/weight?t1=20240101000000&t2=20240119235959" | jq '.'&lt;/code&gt;&lt;/pre&gt;

&lt;h3&gt;2. POST New Weight&lt;/h3&gt;
&lt;pre&gt;&lt;code&gt;curl -X POST "http://localhost:5000/weight" \
-H "Content-Type: application/json" \
-d '{
    "direction": "in",
    "truck": "TRUCK123",
    "containers": "C1,C2",
    "weight": 1000,
    "unit": "kg"
}'&lt;/code&gt;&lt;/pre&gt;

&lt;h3&gt;3. Get Unknown Containers&lt;/h3&gt;
&lt;pre&gt;&lt;code&gt;curl "http://localhost:5000/unknown" | jq '.'&lt;/code&gt;&lt;/pre&gt;

&lt;h2&gt;💾 Data Persistence&lt;/h2&gt;
&lt;p&gt;Data persists between container restarts. To start fresh:&lt;/p&gt;
&lt;pre&gt;&lt;code&gt;docker-compose down -v
docker-compose up --build&lt;/code&gt;&lt;/pre&gt;

&lt;h2&gt;🔧 Troubleshooting&lt;/h2&gt;
&lt;pre&gt;&lt;code&gt;# Check running containers
docker ps | grep mysql

# View MySQL logs
docker-compose logs mysql

# View Flask application logs
docker-compose logs flask_app

# Install jq (Ubuntu/Debian)
sudo apt-get install jq&lt;/code&gt;&lt;/pre&gt;

&lt;h2&gt;🌍 Service Access&lt;/h2&gt;
&lt;ul&gt;
    &lt;li&gt;Flask API: &lt;code&gt;http://localhost:5000&lt;/code&gt;&lt;/li&gt;
    &lt;li&gt;Health Check: &lt;code&gt;http://localhost:5000/health&lt;/code&gt;&lt;/li&gt;
    &lt;li&gt;MySQL Database: &lt;code&gt;localhost:3306&lt;/code&gt;&lt;/li&gt;
&lt;/ul&gt;

&lt;h2&gt;📬 Contributing&lt;/h2&gt;
&lt;ul&gt;
    &lt;li&gt;Fork the repository&lt;/li&gt;
    &lt;li&gt;Create your feature branch (&lt;code&gt;git checkout -b feature/AmazingFeature&lt;/code&gt;)&lt;/li&gt;
    &lt;li&gt;Commit your changes (&lt;code&gt;git commit -m 'Add some AmazingFeature'&lt;/code&gt;)&lt;/li&gt;
    &lt;li&gt;Push to the branch (&lt;code&gt;git push origin feature/AmazingFeature&lt;/code&gt;)&lt;/li&gt;
    &lt;li&gt;Open a Pull Request&lt;/li&gt;
&lt;/ul&gt;

&lt;h2&gt;📄 License&lt;/h2&gt;
&lt;p&gt;This project is licensed under the MIT License - see the &lt;code&gt;LICENSE&lt;/code&gt; file for details.&lt;/p&gt;

&lt;h2&gt;🤝 Acknowledgments&lt;/h2&gt;
&lt;ul&gt;
    &lt;li&gt;Flask&lt;/li&gt;
    &lt;li&gt;MySQL&lt;/li&gt;
    &lt;li&gt;Docker&lt;/li&gt;
&lt;/ul&gt;

&lt;/body&gt;
&lt;/html&gt;
