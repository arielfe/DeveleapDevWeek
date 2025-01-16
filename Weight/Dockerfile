FROM mysql:5.7

# Set root password
ENV MYSQL_ROOT_PASSWORD=root123

# Copy SQL initialization scripts
COPY weightdb.sql /docker-entrypoint-initdb.d/
COPY create_user.sql /docker-entrypoint-initdb.d/

# Expose MySQL default port
EXPOSE 3306
