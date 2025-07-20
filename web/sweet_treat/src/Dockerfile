FROM tomcat:9.0-jdk11

RUN apt-get update && apt-get install -y curl && \
    curl -L -o /usr/local/tomcat/lib/sqlite-jdbc.jar https://repo1.maven.org/maven2/org/xerial/sqlite-jdbc/3.49.1.0/sqlite-jdbc-3.49.1.0.jar && \
    ls -lh /usr/local/tomcat/lib/sqlite-jdbc.jar

COPY ./webapp /usr/local/tomcat/webapps/ROOT
COPY ./directory.db /opt/directory.db
