FROM mambaorg/micromamba:0.15.3
USER root
RUN apt-get update && DEBIAN_FRONTEND=“noninteractive” apt-get install -y --no-install-recommends \
       ca-certificates \
       apache2-utils \
       certbot \
       sudo \
       cifs-utils \
       && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get -y install cron
RUN mkdir /opt/mm_asa_toolbox
RUN chmod -R 777 /opt/mm_asa_toolbox
WORKDIR /opt/mm_asa_toolbox
USER micromamba
COPY environment.yml environment.yml
RUN micromamba install -y -n base -f environment.yml && \
   micromamba clean --all --yes
COPY run.sh run.sh
COPY project_contents project_contents
USER root
RUN chmod a+x run.sh

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install poppler-utils -y

EXPOSE 80

ENTRYPOINT ["streamlit","run"]

CMD ["project_contents/app/MM_Toolbox.py", "--server.port=80", "--server.address=0.0.0.0"]
