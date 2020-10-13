# ================================== BUILDER ===================================
ARG INSTALL_PYTHON_VERSION=3.8
ARG INSTALL_NODE_VERSION=12

FROM node:${INSTALL_NODE_VERSION}-buster-slim AS node
FROM python:${INSTALL_PYTHON_VERSION}-slim-buster AS builder

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y git

COPY --from=node /usr/local/bin/ /usr/local/bin/
RUN true
COPY --from=node /usr/lib/ /usr/lib/
RUN true
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN true

WORKDIR /app

COPY ./bower.json ./package.json package-lock.json ./.bowerrc ./

RUN npm install -g bower
RUN bower install --allow-root

COPY onlineblackboard onlineblackboard
COPY autoapp.py .

# ================================= PRODUCTION =================================
FROM python:${INSTALL_PYTHON_VERSION}-slim-buster as production

WORKDIR /app

RUN useradd -m sid
RUN chown -R sid:sid /app
USER sid
ENV PATH="/home/sid/.local/bin:${PATH}"

COPY . .
COPY --from=builder --chown=sid:sid /app/onlineblackboard/static /app/onlineblackboard/static

COPY requirements requirements
RUN pip install --no-cache --user -r requirements/prod.txt

EXPOSE 5000

ENV FLASK_APP=autoapp.py
ENV FLASK_ENV=production
ENV HOST=0.0.0.0

ENTRYPOINT ["/bin/bash"]
CMD ["-c","gunicorn --bind $HOST:5000 autoapp:app"]
