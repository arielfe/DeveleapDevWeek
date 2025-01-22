FROM mysql:5.7

# Set environment variables
ENV MYSQL_ROOT_PASSWORD=root123
ENV MYSQL_DATABASE=weight
ENV MYSQL_USER=user_weight
ENV MYSQL_PASSWORD=bashisthebest

# Copy initialization SQL scripts
COPY ./app/weightdb.sql /docker-entrypoint-initdb.d/01-weightdb.sql
COPY ./app/create_user.sql /docker-entrypoint-initdb.d/02-create_user.sql

# Use mysql_native_password authentication
CMD ["--default-authentication-plugin=mysql_native_password"]
