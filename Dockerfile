FROM continuumio/miniconda3

# set a directory for the app
RUN mkdir -p /home/5G_car
WORKDIR /home/5G_car

# copy all the files to the container
COPY . .

# install dependencies
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "detectron2", "bin/bash", "-c"]
SHELL ["conda", "run", "--no-capture-output", "-n", "detectron2", "python", "-m", "pip", "install", "'git+https://github.com/facebookresearch/detectron2.git'"]

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "detectron2", "python", "pi_car_basic.py"]