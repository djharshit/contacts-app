FROM python:3.11-alpine

LABEL org.opencontainers.image.source="https://github.com/djharshit/contacts-app"
LABEL maintainer="Harshit M"

ARG PORT=${PORT}

WORKDIR /home/app

COPY . .

RUN wget -q -t3 'https://packages.doppler.com/public/cli/rsa.8004D9FF50437357.key' -O /etc/apk/keys/cli@doppler-8004D9FF50437357.rsa.pub && \
    echo 'https://packages.doppler.com/public/cli/alpine/any-version/main' | tee -a /etc/apk/repositories && \
    apk add --no-cache doppler

RUN chmod +x install.sh && chmod +x run.sh && ./install.sh

EXPOSE ${PORT}

CMD [ "./run.sh" ]