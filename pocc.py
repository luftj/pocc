import os
import argparse
import csv
import json
from itertools import combinations
import math
from tqdm import tqdm

def find_required_class_change(interval, p=1/20):
    d_x = max(interval)-min(interval)
    # c_req = INT(p*d_x)
    # p determined in advance, e.g. 1/20
    # d_x e.g. 20,40,60,...
    pocc = int(p*d_x)
    return pocc

def find_actual_class_change(interval, class_breaks):
    class_breaks = sorted(class_breaks)
    
    # find classes of interval endpoints
    start = 0
    end = 0
    for i,x in enumerate([*class_breaks]):
        if min(interval) > x:
            start = i+1
        if max(interval) > x:
            end = i+1

    return end-start # return class change

def weight(d_c, num_classes):
    # weight non-significant changes heavily to avoid change exaggeration
    return num_classes-1 if d_c==0 else d_c

def POCC(intervals, class_breaks, p):
    c_req = find_required_class_change
    c_ach = find_actual_class_change
    return 1-(sum([weight(c_req(i,p),len(class_breaks)+1)*abs(c_req(i,p)-c_ach(i,class_breaks)) for i in intervals])/sum([weight(c_req(i,p),len(class_breaks)+1)*c_req(i,p) for i in intervals]))

def sweep_line(data, num_classes, p_value=1/20, nodata=-9999):
    intervals = []
    possible_sweep_line_positions = []

    # get all value changes of each time series (intervals) as tuples
    for i in range(len(list(data.values())[0])):
        row = [c[i] for c in data.values()]
        possible_sweep_line_positions.extend(row)
        for i in range(0,len(row)-1):
            if row[i] == nodata or row[i+1] == nodata:
                continue  # filter missing data
            interval = sorted((row[i],row[i+1]))
            intervals.append(interval)
    
    possible_sweep_line_positions = filter(lambda x: x != nodata, possible_sweep_line_positions) # filter missing data
    possible_sweep_line_positions = list(set(possible_sweep_line_positions)) # only unique values
    print("number of possible sweep line positions:", len(possible_sweep_line_positions))

    intervals.sort(key=lambda x: x[0])

    # brute force all possible sweep line combinations
    best_classification = { "POCC": float("-inf") }
    num_possible_combinations = math.comb(len(possible_sweep_line_positions),num_classes-1)
    for positions in tqdm(combinations(possible_sweep_line_positions,num_classes-1), total=num_possible_combinations):
        pocc = POCC(intervals, positions, p_value)

        if pocc > best_classification["POCC"]:
            best_classification = {
                "breaks": sorted(positions),
                "POCC": pocc
            }
    return best_classification

def load_csv(filename, startcolumn: int):
    data = {}
    with open(filename, encoding="utf8") as fr:
        reader = csv.reader(fr, delimiter=";") # to do: autodetect delimiter
        header = next(reader)
        for column in header[startcolumn:]:
            data[column] = []
        for row in reader:
            for col_num, value in enumerate(row[startcolumn:]):
                value = float(value)
                data[header[col_num+startcolumn]].append(value)
    return data

def load_geojson(filename, keys:list[str]=None, values_key:str=None, keys_key=None, nodata=-9999):
    if not keys and (not values_keys):
        raise ValueError("for geojson must provide either keys or vkey")
    
    geometries = []
    with open(filename) as fr:
        json_data = json.load(fr)
        if keys:
            data = {k:[] for k in keys}
        elif keys_key:
            data = {k:[] for k in json_data["features"][0]["properties"][keys_key]}
        else:
            data = {i:[] for i,_ in enumerate(json_data["features"][0]["properties"][values_key])}
        for feature in json_data["features"]:
            for idx,prop in enumerate(data):
                if values_key:
                    data[prop].append(float(feature["properties"][values_key][idx]))
                else:
                    data[prop].append(float(feature["properties"].get(prop, nodata)))
            geometries.append(feature["geometry"])
    return data, geometries

def equidistanct_classifier(data, num_classes, nodata=-9999):
    values = sum(list(data.values()),[])
    values = list(filter(lambda x: x != nodata, values))
    interval_step = (max(values)-min(values))/num_classes
    class_breaks = [min(values)+i*interval_step for i in range(0,num_classes+1)]
    return class_breaks

def classify(values, classifier, **kwargs):
    return classifier(values, **kwargs)

def visualise_geojon(data, geometries, breaks):
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='pocc',
                    description='Calculate change-preserving class breaks for a multi-temporal dataset',
                    epilog='Made by the g2lab of Hafencity University Hamburg. Contact: jonas.luft@hcu-hamburg.de')

    parser.add_argument('filename', help="The csv input file")
    parser.add_argument('classes', type=int, help="number of classes")
    parser.add_argument('-p', type=float, help="desired class difference for 'significant' change. Default: 1/20", default=1/20)
    parser.add_argument('--nodata', help="value that indicates missing data. Default is -9999", default=-9999)
    parser.add_argument('--startcolumn', type=int, help="csv only. the column in which the time series data begins. 0-indexed")
    parser.add_argument('--keys', nargs='+', type=str, help="geojson only. Name of the properties elements that contain data values.")
    parser.add_argument('--vkey', type=str, help="geojson only. Name of the properties element that contains a list of data.")
    # parser.add_argument('--kkey', type=str, help="geojson only. Name of the properties element that contains a list of names for the data columns.")
    args = parser.parse_args()

    # load data file
    if os.path.splitext(args.filename)[-1] == ".csv":
        if args.startcolumn==None:
            raise ValueError("startcolumn needs to be provided for csv files!")
        data = load_csv(args.filename, args.startcolumn)
    elif os.path.splitext(args.filename)[-1] == ".geojson":
        print(args.keys)
        data, geometries = load_geojson(args.filename, keys=args.keys, values_key=args.vkey, nodata=args.nodata)
    else:
        raise NotImplementedError(f"can't read {os.path.splitext(args.filename)[-1]} file. Please supply csv or geojson")

    # show some general stats about values
    print(f"{len(list(data.values())[0])} rows")
    print(f"{len(data)} epochs")
        
    all_values = sum(list(data.values()),[])

    print(f"value range: [{min(all_values)}-{max(all_values)}]")
    
    # classify data
    class_breaks_equidistant = classify(data, equidistanct_classifier, num_classes=args.classes, nodata=args.nodata)
    class_breaks_pocc = classify(data, sweep_line, num_classes=args.classes, p_value=args.p, nodata=args.nodata)

    print("equidistant:",class_breaks_equidistant)
    print("pocc-based:",class_breaks_pocc)

    if os.path.splitext(args.filename)[-1] == "geojson":
        visualise_geojon(data, geometries, class_breaks_pocc["breaks"])