FROM docker.io/library/python:3.14.4-slim
RUN apt-get update && apt-get install -y curl
WORKDIR /home/paris
COPY . .
RUN bash ./install.sh
RUN pip install -r requirements.txt
CMD ["bash", "bin/run.sh"]
