# Builder Image

FROM python:3.12-alpine AS builder

WORKDIR /app

COPY . .

RUN sh install.sh

# Runner Image

FROM python:3.12-alpine AS runnner

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app /app

WORKDIR /app

RUN apk add --no-cache curl gnupg mariadb-connector-c-dev && \
    (curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh || wget -t 3 -qO- https://cli.doppler.com/install.sh) | sh

LABEL org.opencontainers.image.source="https://github.com/djharshit/contacts-app"
LABEL maintainer="Harshit M"

ARG PORT=5000

EXPOSE ${PORT}

CMD [ "sh", "run.sh" ]