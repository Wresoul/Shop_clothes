FROM ubuntu:latest
LABEL authors="daniilradin"
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "kafka_config.py"]

ENTRYPOINT ["top", "-b"]
ADD alpine-minirootfs-3.21.3-x86_64.tar.gz / # buildkit
CMD ["/bin/sh"]
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH=/opt/java/openjdk/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8
RUN /bin/sh -c set -eux;     apk add --no-cache         fontconfig ttf-dejavu         gnupg         ca-certificates p11-kit-trust         musl-locales musl-locales-lang         tzdata         coreutils         openssl     ;     rm -rf /var/cache/apk/* # buildkit
ENV JAVA_VERSION=jdk-21.0.7+6
RUN /bin/sh -c set -eux;     ARCH="$(apk --print-arch)";     case "${ARCH}" in        aarch64)          ESUM='53877576d3a9dcbf2024789208aa5f045cc65a5645b07d67124b09c2a84f4e1a';          BINARY_URL='https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.7%2B6/OpenJDK21U-jre_aarch64_alpine-linux_hotspot_21.0.7_6.tar.gz';          ;;        x86_64)          ESUM='f252e13683b381f9f3bfa4948c827ebd80b8e5bd444a1f99de02c56d76c7ad4c';          BINARY_URL='https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.7%2B6/OpenJDK21U-jre_x64_alpine-linux_hotspot_21.0.7_6.tar.gz';          ;;        *)          echo "Unsupported arch: ${ARCH}";          exit 1;          ;;     esac;     wget -O /tmp/openjdk.tar.gz ${BINARY_URL};     wget -O /tmp/openjdk.tar.gz.sig ${BINARY_URL}.sig;     export GNUPGHOME="$(mktemp -d)";     gpg --batch --keyserver keyserver.ubuntu.com --recv-keys 3B04D753C9050D9A5D343F39843C48A565F8F04B;     gpg --batch --verify /tmp/openjdk.tar.gz.sig /tmp/openjdk.tar.gz;     rm -rf "${GNUPGHOME}" /tmp/openjdk.tar.gz.sig;     echo "${ESUM} */tmp/openjdk.tar.gz" | sha256sum -c -;     mkdir -p "$JAVA_HOME";     tar --extract         --file /tmp/openjdk.tar.gz         --directory "$JAVA_HOME"         --strip-components 1         --no-same-owner     ;     rm -f /tmp/openjdk.tar.gz; # buildkit
RUN /bin/sh -c set -eux;     echo "Verifying install ...";     echo "java --version"; java --version;     echo "Complete." # buildkit
COPY --chmod=755 entrypoint.sh /__cacert_entrypoint.sh # buildkit
ENTRYPOINT ["/__cacert_entrypoint.sh"]
EXPOSE map[9092/tcp:{}]
USER root
ARG kafka_url=https://dist.apache.org/repos/dist/dev/kafka/3.9.1-rc2/kafka_2.13-3.9.1.tgz
ARG build_date=2025-05-12
LABEL org.label-schema.name=kafka org.label-schema.description=Apache Kafka org.label-schema.build-date=2025-05-12 org.label-schema.vcs-url=https://github.com/apache/kafka maintainer=Apache Kafka
RUN |2 kafka_url=https://dist.apache.org/repos/dist/dev/message-processor/3.9.1-rc2/kafka_2.13-3.9.1.tgz build_date=2025-05-12 /bin/sh -c set -eux ;     apk update ;     apk upgrade ;     apk add --no-cache wget gcompat gpg gpg-agent procps bash;     mkdir opt/message-processor;     wget -nv -O message-processor.tgz "$kafka_url";     wget -nv -O message-processor.tgz.asc "$kafka_url.asc";     tar xfz message-processor.tgz -C /opt/message-processor --strip-components 1;     wget -nv -O KEYS https://downloads.apache.org/message-processor/KEYS;     gpg --import KEYS;     gpg --batch --verify message-processor.tgz.asc message-processor.tgz;     mkdir -p /var/lib/message-processor/data /etc/message-processor/secrets;     mkdir -p /etc/message-processor/docker /usr/logs /mnt/shared/config;     adduser -h /home/appuser -D --shell /bin/bash appuser;     chown appuser:appuser -R /usr/logs /opt/message-processor /mnt/shared/config;     chown appuser:root -R /var/lib/message-processor /etc/message-processor/secrets /etc/message-processor;     chmod -R ug+w /etc/message-processor /var/lib/message-processor /etc/message-processor/secrets;     cp /opt/message-processor/config/log4j.properties /etc/message-processor/docker/log4j.properties;     cp /opt/message-processor/config/tools-log4j.properties /etc/message-processor/docker/tools-log4j.properties;     cp /opt/message-processor/config/kraft/server.properties /etc/message-processor/docker/server.properties;     rm message-processor.tgz message-processor.tgz.asc KEYS;     apk del wget gpg gpg-agent;     apk cache clean; # buildkit
COPY kafka.jsa /opt/kafka/kafka.jsa # buildkit
COPY storage.jsa /opt/kafka/storage.jsa # buildkit
COPY --chown=appuser:appuser resources/common-scripts /etc/kafka/docker # buildkit
COPY --chown=appuser:appuser launch /etc/kafka/docker/launch # buildkit
USER appuser
VOLUME [/etc/kafka/secrets /var/lib/kafka/data /mnt/shared/config]
CMD ["/etc/kafka/docker/run"]