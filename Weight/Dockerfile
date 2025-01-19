FROM mysql:5.7

# Add MySQL GPG key and update packages
RUN rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022 && \
    yum clean all && \
    yum update -y --nogpgcheck && \
    yum install -y jq curl --nogpgcheck

# Set root password
ENV MYSQL_ROOT_PASSWORD=root123

# Copy SQL initialization scripts
COPY weightdb.sql /docker-entrypoint-initdb.d/
COPY create_user.sql /docker-entrypoint-initdb.d/

# Expose MySQL default port
EXPOSE 3306
