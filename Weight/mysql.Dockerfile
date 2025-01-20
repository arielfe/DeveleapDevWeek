FROM mysql:5.7

# Set environment variables
ENV MYSQL_ROOT_PASSWORD=root123
ENV MYSQL_DATABASE=weight
ENV MYSQL_USER=nati
ENV MYSQL_PASSWORD=bashisthebest

# Copy initialization SQL script
COPY ./app/weightdb.sql /docker-entrypoint-initdb.d/init.sql

# Use mysql_native_password authentication
CMD ["--default-authentication-plugin=mysql_native_password"]