FROM jupyter/base-notebook
 
USER root
RUN apt-get update && apt-get install -y build-essential g++ libgl1-mesa-glx libx11-6
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /src 
WORKDIR /src

