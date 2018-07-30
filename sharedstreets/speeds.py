from __future__ import print_function
import argparse
from . import tile
from . import speeds_pb2

protobuf_classes = [
    speeds_pb2.SharedStreetsWeeklySpeeds
    ]


parser = argparse.ArgumentParser(description='Read SharedStreets Speed protobuf and convert to CSV')
parser.add_argument('filename', help='Protobuf SharedStreets speed data')

def flatten_weekly_speed_histogram(tileContent):
    speedObservations = []

    count = 0;
    for item in tile.read_objects(0, tileContent, speeds_pb2.SharedStreetsWeeklySpeeds):
        count += 1
        for period in item.speedsByPeriod:
            for frame in period.histogram:
                for pos in range(0, len(frame.speedBin)):
                    speedObservations.append([item.referenceId, period.periodOffset[0], frame.speedBin[pos], frame.observationCount[pos]])

    return speedObservations;
