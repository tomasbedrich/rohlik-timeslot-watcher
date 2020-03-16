FROM python:3.8

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pip3 install pipenv
RUN pipenv install --deploy --system

COPY watcher.py ./

ENTRYPOINT ["python3", "/app/watcher.py"]
