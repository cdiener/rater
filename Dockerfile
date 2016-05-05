FROM continuumio/miniconda3

COPY . /app
WORKDIR /app

RUN conda install -y --file requirements.txt && conda remove mkl && conda clean -tipsy
RUN rm data/*.db && python -c "from app import init_db; init_db()"
EXPOSE 5000

CMD [ "python", "app.py" ]
