FROM python:3.11-slim

RUN apt-get update
RUN apt-get install -y --no-install-recommends openjdk-21-jdk git bash procps vim lsof

RUN git clone https://github.com/deringezgin/COM407-FinalProject
WORKDIR /COM407-FinalProject
RUN chmod +x setup.sh run_sharp_agent.sh
RUN ./setup.sh noenv

CMD ["/bin/bash"]
