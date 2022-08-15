FROM continuumio/miniconda3

# set a directory for the app

#RUN mkdir -p /home/5G_car
#WORKDIR /home/5G_car

# copy all the files to the container
#COPY . .

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . $APP_HOME

# install dependencies
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "app", "/bin/bash", "-c"]

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

ENTRYPOINT ["conda", "run", "-n", "app", "python", "main.py", $ENV1]