#!/bin/bash
/opt/conda/bin/conda update conda && \
/opt/conda/bin/conda update --all && \
# /opt/conda/bin/conda create --yes -n py36 python=3.6 && \
# source ~/.bashrc && \
# /opt/conda/bin/conda activate py36 && \
/opt/conda/bin/conda install --yes -c openbabel openbabel && \
/opt/conda/bin/conda install --yes -c anaconda gunicorn && \
/opt/conda/bin/conda install --yes -c bioconda mysqlclient && \
/opt/conda/bin/conda install --yes -c anaconda mysql-python
