FROM continuumio/miniconda3

# set a directory for the app

RUN mkdir -p /home/5G_car
WORKDIR /home/5G_car
COPY . .

RUN apt-get update && apt-get install -y python3-opencv

# install dependencies
RUN conda env create -f environment.yml 
SHELL ["conda", "run", "-n", "pi_car", "/bin/bash", "-c"]


RUN (apt-get autoremove -y; \
     apt-get autoclean -y)  

# RUN apt-get update
# RUN apt-get install ffmpeg libsm6 libxext6  -y

ENTRYPOINT ["conda", "run", "-n", "pi_car", "python", "main.py"]