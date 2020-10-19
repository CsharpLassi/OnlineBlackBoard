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

COPY src/obb obb
COPY src/wsgi.py .

# ================================= PRODUCTION =================================
FROM python:${INSTALL_PYTHON_VERSION}-slim-buster as production

WORKDIR /app

RUN useradd -m sid
RUN chown -R sid:sid /app
USER sid
ENV PATH="/home/sid/.local/bin:${PATH}"

COPY requirements requirements
RUN pip install --no-cache --user -r requirements/prod.txt

COPY src/obb obb
COPY src/wsgi.py wsgi.py
COPY run.sh .
COPY --from=builder --chown=sid:sid /app/src/obb/static /app/obb/static

EXPOSE 5000

ENV FLASK_APP=src/wsgi.py
ENV FLASK_ENV=production
ENV HOST=0.0.0.0
ENV PREFERRED_URL_SCHEME=http
ENV SECRET_KEY=you-will-never-guess
ENV DATABASE_URL="sqlite:////app/app.db"

ENTRYPOINT ["/bin/bash"]
CMD ["-c","./run.sh"]
