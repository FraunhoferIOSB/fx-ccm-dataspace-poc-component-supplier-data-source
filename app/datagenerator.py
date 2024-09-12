from pathlib import Path
import json
import random
import time
import uuid
from typing import Annotated

from fastapi import FastAPI

from app.vseparser import parse_vse

app = FastAPI()

directory = Path(__file__).parent


@app.get("/fx/")
def get_root():
    return {"IFM Data Generator (VSE & Moneo) for the TP2.04 & TP4.1 POC."}


@app.get("/fx/vse_idat/")
def get_vse_idat(ip: Annotated[str, "IP"] = "192.168.0.123",
                 port: Annotated[int, "Port"] = "8080"):
    """
        Parameters:
        ip   - IP of the VSE
        port - Port of the VSE
    """
    file_path = directory / 'data' / "Rawdata_BearingUnit VSE100.idat"
    with open(file_path, 'rb') as f:
        vse = parse_vse(f.read())
        return vse


@app.get("/fx/vse_opc/")
def get_vse_opc(ip: Annotated[str, "IP"] = "192.168.0.123",
                port: Annotated[int, "Port"] = "8080"):
    """
        Parameters:
        ip   - IP of the VSE
        port - Port of the VSE
    """
    data = load_data('vse_gen_opc.json')
    data['ConnectionSettings'] = f"{ip}:{port}"
    return data


@app.get("/fx/moneo_unit/")
def get_moneo_unit(thing_id: Annotated[uuid.UUID, "thingId"] = "e5e34268-2198-4c25-9396-fc7da8fb48cd",
                   property_set_name: Annotated[str, "propertySetName"] = "pdin-Temperature"):
    """
        Parameters:
        thingId         - Moneo intern ID for the sensor
        propertySetName - Name of the property from the sensor
    """
    data = load_data('moneo_unit.json')
    return data


@app.get("/fx/moneo_data/")
def get_moneo_data(thing_id: Annotated[uuid.UUID, "thingId"] = "e5e34268-2198-4c25-9396-fc7da8fb48cd",
                   property_set_name: Annotated[str, "propertySetName"] = "pdin-Temperature",
                   count: Annotated[int, "count"] = 10):
    """
        Parameters:
        thingId         - Moneo intern ID for the sensor
        propertySetName - Name of the property from the sensor
        count           - Amount of the past values
    """
    return {"count": count, "values": gen_moneo_data(count)}


def load_data(filename: str):
    file_path = directory / 'data' / filename
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def gen_moneo_data(amount):
    current_time = int(time.time() * 1000)
    data = []
    value = 29.1

    for i in range(amount):
        entry_time = current_time - (i * 1000)
        adjustment = round(random.choice([-0.1, 0, 0.1]), 1)
        value = round(value + adjustment, 1)
        entry = {
            "_v": value,
            "time": entry_time,
            "isAverageValue": True,
            "MinValue": round(value - 0.1, 1),
            "MaxValue": round(value + 0.1, 1)
        }
        data.append(entry)

    return data