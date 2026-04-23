FROM hrchlhck/actions-runner

USER root

RUN APT update && apt install nikto -t

USER devsecops
