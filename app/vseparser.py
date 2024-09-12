import math
import struct


# Trim lists from zeros to keep result short
def trim_zeros_custom(arr):
    tolerance = 1e-9
    arr = list(filter(lambda x: not math.isclose(x, 0.0, abs_tol=tolerance), arr))
    arr.reverse()
    arr = list(filter(lambda x: not math.isclose(x, 0.0, abs_tol=tolerance), arr))
    arr.reverse()
    return arr


# Corrected function to parse the header
def parse_ves004_header(data):
    header_format = "20s 7I 512s 80s 250I 20s"
    header_size = struct.calcsize(header_format)
    header_data = struct.unpack(header_format, data[:header_size])

    header = {
        "yosiVersion": header_data[1],
        "dataVersion": header_data[2],
        "dataSize": header_data[3],
        "id": header_data[4],
        "plugIn": header_data[5],
        "type": header_data[6],
        "subType": header_data[7],
        "name": header_data[8].decode('utf-16').replace("\x00", ""),
        "uuid": header_data[9].decode('utf-16').replace("\x00", ""),
    }
    return header, header_size


def parse_df_header(data):
    header_format = "6I 3Q I 207I"
    header_size = struct.calcsize(header_format)
    header_data = struct.unpack(header_format, data[:header_size])
    header = {
        "version": header_data[0],
        "yosemite": header_data[1],
        "type": header_data[2],
        "dataSourceCount": header_data[3],
        "recordSize": header_data[4],
        "timezone": header_data[5],
        "creationTime": header_data[6],
        "timeRangeStart": header_data[7],
        "timeRangeEnd": header_data[8],
        "rawDataMetaData": header_data[9],
        "m_reserved": header_data[10]
    }
    return header, header_size


# Function to parse a data source safely and check field alignments
def parse_dfdata_source(data):
    source_format = "2Q 4I 3Q I 256s 256s 256s 256s 7f I 256s I 256s 256s I 416s"
    basic_size = struct.calcsize(source_format)

    if len(data) < basic_size:
        raise ValueError(
            f"Data buffer too small for data source, expected at least {basic_size} bytes, got {len(data)}")

    source_data = struct.unpack(source_format, data[:basic_size])

    data_source = {
        "handle": source_data[0],
        "parent": source_data[1],
        "plugIn": source_data[2],
        "type": source_data[3],
        "subType": source_data[4],
        "engUnit": source_data[5],
        "valueID": source_data[6],
        "address": source_data[7],
        "flags": source_data[8],
        "deviceID": source_data[9],
        "deviceUUID": source_data[10].decode('utf-16').replace("\x00", ""),
        "name": source_data[11].decode('utf-16').replace("\x00", ""),
        "inputName": source_data[12].decode('utf-16').replace("\x00", ""),
        "unitString": source_data[13].decode('utf-16').replace("\x00", ""),
        "parameters": trim_zeros_custom(list(source_data[14:21])),
        "objectType": source_data[21],
        "deviceName": source_data[22].decode('utf-16').replace("\x00", ""),
        "deviceType": source_data[23],
        "deviceSerialNumber": source_data[24].decode('utf-16').replace("\x00", ""),
        "deviceAddress": source_data[25].decode('utf-16').replace("\x00", ""),
        "devSize": source_data[26],
        "devData": 0 if source_data[26] == 0 else source_data[27].hex()
    }

    return data_source, basic_size


def parse_dfdata_stream(data):
    stream_format = "Q I Q I 2I 4096f"
    stream_size = struct.calcsize(stream_format)

    if len(data) < stream_size:
        raise ValueError(f"Data buffer too small for data stream, expected {stream_size} bytes, got {len(data)}")

    stream_data = struct.unpack(stream_format, data[:stream_size])

    data_stream = {
        "dataSourceHandle": stream_data[0],
        "flags": stream_data[1],
        "timestamp": stream_data[2],
        "valueCount": stream_data[3],
        "sampleRateDivider": stream_data[4],
        "engUnit": stream_data[5],
        "values": trim_zeros_custom(list(stream_data[6:]))
    }

    return data_stream, stream_size


def parse_vse(data):
    # Parse the headers
    vse_header, vse_header_offset = parse_ves004_header(data)
    df_header, df_header_offset = parse_df_header(data[vse_header_offset:])

    offset = vse_header_offset + df_header_offset

    data_sources = []
    data_source_count = df_header["dataSourceCount"]

    # Parse the dataSources
    for i in range(data_source_count):
        if offset >= len(data):
            print(f"Reached end of file before parsing all data sources. Parsed {i} data sources.")
            break
        data_source, source_size = parse_dfdata_source(data[offset:])
        data_sources.append(data_source)
        offset += source_size

    # Parse the raw data stream
    data_stream = None
    if offset < len(data):
        try:
            data_stream, stream_size = parse_dfdata_stream(data[offset:])
            offset += stream_size
        except ValueError as e:
            print(f"Error parsing raw data stream: {e}")

    # Pack result
    return {
        "header": {
            "ves": vse_header,
            "df": df_header
        },
        "dataSources": data_sources,
        "rawDataStream": data_stream
    }
