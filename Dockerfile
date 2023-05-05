FROM nvcr.io/nvidia/paddlepaddle:22.08-py3

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime && \
    echo "America/New_York" > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    software-properties-common -y \
    libgl1-mesa-glx -y

copy requirements.txt ./requirements.txt

## Install production dependencies.
RUN pip install -r requirements.txt

RUN pip install --upgrade protobuf==3.20.0

## Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

EXPOSE 5000

CMD exec gunicorn --bind :5000 --workers 1 --threads 8 --timeout 0 main:app