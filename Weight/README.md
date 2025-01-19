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
