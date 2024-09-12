# simple BASE-Image
FROM python:3.10.11

# working directory for te container
WORKDIR /fx_data_generator

# Install requirements
COPY ./req.txt  /fx_data_generator/req.txt
RUN pip install --no-cache-dir --upgrade -r /fx_data_generator/req.txt

# Run "API-APP"
COPY ./app /fx_data_generator/app
CMD ["uvicorn", "app.datagenerator:app", "--host", "0.0.0.0", "--port", "80"]
# NOTE: we might want to change the port-cfg depending on the deployment
#       on the individual k8s-clusters (Arno's cluster, Catena cluster, SFH ...) 