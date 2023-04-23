FROM postgres:latest

ENV POSTGRES_DB sales
ENV POSTGRES_USER test
ENV POSTGRES_PASSWORD 2023Docker

COPY init.sql /docker-entrypoint-initdb.d/
