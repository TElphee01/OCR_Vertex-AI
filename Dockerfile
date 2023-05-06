FROM nvcr.io/nvidia/paddlepaddle:22.08-py3

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt
RUN pip install --upgrade protobuf==3.20.0

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED True

RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata && \
    ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime && \
    echo "America/New_York" > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata \
    software-properties-common -y \
    libgl1-mesa-glx -y

## Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

EXPOSE 8080

CMD exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0 --log-level debug main:app
