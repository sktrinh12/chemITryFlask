FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive 

# Install dependencies
RUN apt-get update && \
	apt-get -y upgrade && \
	apt-get install -y git \
	wget

# download miniconda and install
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
	/bin/bash ~/miniconda.sh -b -p /opt/conda && \
	rm ~/miniconda.sh && \
	/opt/conda/bin/conda clean --all && \
	echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc 

ADD chemITry-pkgs.yml /opt/chemITry-pkgs.yml 
RUN /opt/conda/bin/conda env create -f /opt/chemITry-pkgs.yml
ENV PATH /opt/conda/envs/py36/bin:$PATH

# Add code
ADD . /opt/chemITry/
COPY cmd.sh /opt/chemITry/cmd.sh
RUN chmod +x /opt/chemITry/cmd.sh 
WORKDIR /opt/chemITry
EXPOSE 5000
CMD python run.py
