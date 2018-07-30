from __future__ import print_function
import argparse
from . import tile
from . import linear_references_pb2

protobuf_classes = [
    linear_references_pb2.SharedStreetsWeeklyBinnedLinearReferences
    ]


parser = argparse.ArgumentParser(description='Read SharedStreets binned linear reference protobuf and convert to CSV')
parser.add_argument('filename', help='Protobuf SharedStreets binned linear reference data')

def flatten_binned_events(tileContent):
    binnedObservations = []

    count = 0;
    for item in tile.read_objects(0, tileContent, linear_references_pb2.SharedStreetsWeeklyBinnedLinearReferences):
        count += 1
        for binPos in range(0, len(item.binPosition)):
            linearBin = item.binnedPeriodicData[binPos]
            for periodPos in range(0, len(linearBin.bins)):
                binData = linearBin.bins[periodPos]
                binnedObservations.append([item.referenceId, item.numberOfBins, binPos+1, binData.dataType[0], binData.count[0], binData.value[0]])
                
    return binnedObservations;
