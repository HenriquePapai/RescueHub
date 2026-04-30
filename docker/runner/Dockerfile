FROM hrchlhck/actions-runner

USER root

RUN apt update && apt install -y nikto python3-pip && pip3 install bandit

USER devsecops
