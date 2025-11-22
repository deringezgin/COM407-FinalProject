FROM python:3.11-slim

RUN apt-get update
RUN apt-get install -y --no-install-recommends openjdk-21-jdk git bash procps xvfb xauth

WORKDIR /ci_final
RUN git clone https://github.com/deringezgin/ci_final.git .
RUN chmod +x run_gui.sh

RUN git clone https://github.com/SimonLucas/planet-wars-rts.git planet-wars-rts && \
    cd planet-wars-rts && \
    git apply ../planet-wars-rts-addGUI.patch && \
    ./gradlew :app:build -x test

ENV PYTHONPATH=/ci_final/planet-wars-rts/app/src/main/python

RUN pip install -r planet-wars-rts/app/src/main/python/requirements.txt && \
    pip install numpy torch cma pyyaml

CMD ["/bin/bash"]
