# https://confluence.godaddy.com/display/AS/Onboarding+How+To
FROM 764525110978.dkr.ecr.us-west-2.amazonaws.com/amazonlinux:2

USER root

RUN yum install -y python3 shadow-utils unzip wget && \
    yum clean all && \
    rm -rf /var/cache/yum && \
    useradd -m -d /opt/gophish -s /bin/bash app

USER app

RUN python3 -m pip install --user --upgrade pip && \
    python3 -m pip install --user --no-warn-script-location awscli boto3

WORKDIR /opt/gophish

RUN wget --no-check-certificate https://github.com/gophish/gophish/releases/download/v0.11.0/gophish-v0.11.0-linux-64bit.zip && \
    unzip gophish-v0.11.0-linux-64bit.zip && \
    rm gophish-v0.11.0-linux-64bit.zip && \
    chmod +x gophish

COPY run.py .

RUN mkdir -p static/endpoint && echo "OK" > static/endpoint/healthcheck.html

EXPOSE 3333 8443

CMD ["./run.py"]
