FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
# FROM python:3.9

WORKDIR /app/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/
COPY ./requirements.txt /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "poetry run pip install -r requirements.txt"

# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG INSTALL_JUPYTER=false
RUN bash -c "if [ $INSTALL_JUPYTER == 'true' ] ; then pip install jupyterlab ; fi"

COPY ./ /app
# # RUN rm /start-reload.sh
# COPY ./scripts/start-reload.sh /start-reload.sh
ENV PYTHONPATH=/app/app/
