ARG TAG="master"
ARG DOCKER_REGISTRY_HOST
FROM ${DOCKER_REGISTRY_HOST}/base/configuration:master as conf
FROM python:3.7

COPY --from=conf /build/env /local/env

RUN mkdir -p /local/oc_portal_commons/dist 
COPY . /local/oc_portal_commons/

WORKDIR /local/oc_portal_commons/ 

RUN /bin/bash -c 'export $(cat /local/env)'

RUN chgrp -R 0 /local/oc_portal_commons && \
    chmod -R g=u /local/oc_portal_commons
RUN python3 -m pip install $(pwd) && \
    python3 -m unittest discover 
RUN python3 ./setup.py bdist_wheel 

