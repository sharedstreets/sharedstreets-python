from __future__ import print_function
import argparse
import math
import copy
from . import tile
from . import linear_references_pb2
from google.protobuf.internal.encoder import _VarintEncoder

from collections import defaultdict


protobuf_classes = [
    linear_references_pb2.SharedStreetsWeeklyBinnedLinearReferences
    ]

parser = argparse.ArgumentParser(description='Read SharedStreets binned linear reference protobuf and convert to CSV')
parser.add_argument('filename', help='Protobuf SharedStreets binned linear reference data')

MAX_SCALING_LCM_FACTOR = 10 # caps LCM at n * greater(x, y)

def least_common_multiple(x, y):
    # choose the greater number
    if x > y:
        greater = x
    else:
        greater = y
    
    max_factor = greater * MAX_SCALING_LCM_FACTOR
    
    while True:

       if greater >= max_factor:
           lcm = greater
           break

       if((greater % x == 0) and (greater % y == 0)):
           lcm = greater
           break

       greater += 1
    
    return lcm

def get_bin_count(ref_length, bin_size):
    num_bins = math.floor(ref_length / bin_size) + 1

class BinnedLinearReference:

    def __init__(self, item):
        self.reference_id = item.referenceId

        if item.scaledCounts:
            self.scaled_counts = item.scaledCounts
        else: 
            self.scaled_counts = False 

        self.reference_length = float(item.referenceLength) / 100
        self.number_of_bins = item.numberOfBins
        
        if type(item) is linear_references_pb2.SharedStreetsWeeklyBinnedLinearReferences:
            self.weeklyCylce = True
        
            # data indexed as a multi-dimentional array {dataType}[binPosition][periodOffset] 
            self.data = {}

            for bin_index in range(0, len(item.binPosition)):

                bin_position = item.binPosition[bin_index]
                linear_bin = item.binnedPeriodicData[bin_index]

                for period_index in range(0, len(linear_bin.periodOffset)):

                    period_offset = linear_bin.periodOffset[period_index]
                    bin_data = linear_bin.bins[period_index]

                    for data_index in range(0, len(bin_data.dataType)):

                        data_type = bin_data.dataType[data_index]
                        data_count = bin_data.count[data_index]
                        data_value = bin_data.value[data_index]


                    self.data.setdefault(data_type, {}).setdefault(bin_position, {})[period_offset] = {"count": data_count, "value": data_value} 

    def __str__(self):
        return self.reference_id + ': ' + str(self.reference_length) + 'm / ' +  str(self.number_of_bins) + ' bins -> ' + '{0:.3g}'.format(self.get_bin_length()) + ' m/bin'

    def get_bin_length(self):
        return self.reference_length / self.number_of_bins

    def get_max_count(self):
        max_count = 0

        for data_type in self.data:
            for bin_pos in self.data[data_type]:
                for bin_period in self.data[data_type][bin_pos]:
                    if 'count' in self.data[data_type][bin_pos][bin_period] and self.data[data_type][bin_pos][bin_period]['count'] > max_count:
                        max_count = self.data[data_type][bin_pos]['count']
        
        return max_count

    def scale_counts(self, max_count):

        if max_count == None:
            max_count = self.get_max_count()

        self.scaled_counts = True

        for data_type in self.data:
            for bin_pos in self.data[data_type]:
                for bin_period in self.data[data_type][bin_pos]:
                    if 'count' in self.data[data_type][bin_pos][bin_period] and self.data[data_type][bin_pos][bin_period]['count'] > 0:
                        self.data[data_type][bin_pos]['count']  = float(self.data[data_type][bin_pos]['count']) / float(max_count)


    # resize bins works only with scaled counts
    def resize_bins(self, new_bin_length, max_count):

        data_copy = copy.deepcopy(self.data)

        return


    def merge(self, new_data):

        if self.reference_id != new_data.reference_id:
            raise ValueError('References IDs do not match')
        
        if self.nubmer_of_bins != new_data.nubmer_of_bins:
            raise ValueError('Bin count does not match')

        for data_type in self.data:
            for bin_pos in self.data[data_type]:
                for bin_period in self.data[data_type][bin_pos]:

                    existing_count = self.data[data_type][bin_pos][bin_period]['count']
                    existing_value = self.data[data_type][bin_pos][bin_period]['value']
                    if data_type in new_data and bin_pos in new_data[data_type] and bin_period in new_data[data_type][bin_pos]: 

                        new_count = new_data.data[data_type][bin_pos][bin_period]['count']
                        new_value = new_data.data[data_type][bin_pos][bin_period]['value']
                        
                        self.data[data_type][bin_pos][bin_period]['count'] = existing_count + new_count
                        self.data[data_type][bin_pos][bin_period]['value'] = existing_value + new_value


    def filter(self, min_count):

        data_copy = copy.deepcopy(self.data)

        for data_type in self.data:
            for bin_pos in self.data[data_type]:
                for bin_period in self.data[data_type][bin_pos]:
                    if 'count' in self.data[data_type][bin_pos][bin_period] and self.data[data_type][bin_pos][bin_period]['count'] < min_count:
                        data_copy[data_type][bin_pos].pop(bin_period, None)
                    
                    if len(data_copy[data_type][bin_pos]) == 0:
                        data_copy[data_type][bin_pos].pop(bin_period, None)
                if len(data_copy[data_type]) == 0:
                    data_copy[data_type].pop(bin_pos, None)
            if len(data_copy) == 0:
                data_copy.pop(data_type, None)
        
        self.data = data_copy

    def print(self):

        for data_type in self.data:
            print(self.reference_id + ': ' + data_type)
            for bin_pos in self.data[data_type]:
                print('\t ' + str(bin_pos))
                for bin_period in self.data[data_type][bin_pos]:
                    print('\t\t ' + str(bin_period))
                    for attribute in self.data[data_type][bin_pos][bin_period]:
                        print('\t\t\t ' +  str(attribute) + ":" + str(self.data[data_type][bin_pos][bin_period][attribute]))

    def toPbf(self):

        pbfBinnedLinearReference = linear_references_pb2.SharedStreetsWeeklyBinnedLinearReferences()

        pbfBinnedLinearReference.referenceId = self.reference_id
        pbfBinnedLinearReference.referenceLength = int(round(self.reference_length * 100)) 
        pbfBinnedLinearReference.numberOfBins = self.number_of_bins
        pbfBinnedLinearReference.scaledCounts = self.scaled_counts

        pbfData = {}

        # pivot data to pbf format
        for data_type in self.data:
            for bin_pos in self.data[data_type]:
                for bin_period in self.data[data_type][bin_pos]:
                    
                    data_count = self.data[data_type][bin_pos][bin_period]['count']
                    data_value = self.data[data_type][bin_pos][bin_period]['value']

                    # TODO handle multi data-type writes
                    pbfData.setdefault(bin_pos, {})[bin_period] = {"data_type": data_type, "count": data_count, "value": data_value} 

        # write data to pbf 
        for bin_pos in pbfData:
            bin_position = pbfBinnedLinearReference.binPosition.append(bin_pos)
            bin_position_data = pbfBinnedLinearReference.binnedPeriodicData.add()
            for bin_period in pbfData[bin_pos]:
                bin_position_data.periodOffset.append(bin_period)
                bin_period_data = bin_position_data.bins.add()

                bin_period_data.dataType.append(pbfData[bin_pos][bin_period]['data_type'])
                bin_period_data.count.append(pbfData[bin_pos][bin_period]['count'])
                bin_period_data.value.append(pbfData[bin_pos][bin_period]['value']) 
        

        return pbfBinnedLinearReference.SerializeToString()


    def flatten(self):
        flattend_observations = []
        for data_type in self.data:
            for bin_pos in self.data[data_type]:
                for bin_period in self.data[data_type][bin_pos]:
                    count = self.data[data_type][bin_pos][bin_period]['count']
                    value = self.data[data_type][bin_pos][bin_period]['value']
                    flattened_observation = [self.reference_id, self.reference_length, self.number_of_bins, bin_pos, bin_period, data_type, count, value]
                    flattend_observations.append(flattened_observation)

        return flattend_observations


# generates a length encoded stream of pbf
def generate_pbf(output_file, binned_observations):
    
    for binned_reference in binned_observations:

        pbf_data = binned_reference.toPbf()
        size_of_data = len(pbf_data)
        _VarintEncoder()(output_file.write, size_of_data, True)
        output_file.write(pbf_data)
        #output.append(pbf_data)



def load_binned_events(tileContent):
    binned_observations = []

    for item in tile.read_objects(0, tileContent, linear_references_pb2.SharedStreetsWeeklyBinnedLinearReferences):
        binned_reference = BinnedLinearReference(item)
        binned_observations.append(binned_reference)

    return binned_observations
