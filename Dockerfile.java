#build stage
FROM maven:3.9-eclipse-temurin-17-alpine AS builder
WORKDIR /build
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn clean package -DskipTests

#runtime stage
FROM eclipse-temurin:17-jdk-alpine

WORKDIR /app

# Copy the JAR from the build stage
COPY --from=builder /build/target/concore-*.jar /app/concore.jar
EXPOSE 3000
CMD ["java", "-jar", "/app/concore.jar"]