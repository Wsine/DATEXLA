FROM moul/armhf-python-dev
RUN pip install redis
RUN pip install requests
COPY worker.py /
CMD ["python", "worker.py"]
