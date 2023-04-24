FROM alpine:latest
RUN apk add --no-cache python3 py3-pip

WORKDIR /app
COPY ./requirements.txt /app

RUN pip install -r ./requirements.txt
COPY ./src/ /app/

ENTRYPOINT [ "python3", "main.py" ]