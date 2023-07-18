# POCC

A tool for change-preserving classification of multi-temporal (spatial) data.

---

## Introduction

POCC is a method for data classification, which can reduce these effects of change loss and change exaggeration as far as possible. The classification uses a sweep line algorithm, whose optimal solution is determined with the help of a measure called Preservation Of Change Classes 
(POCC). By assigning weights during computation of this measure, different tasks or 
change analyses (e.g. emphasize only highly significant changes) can be processed. 
As a side effect, such constraints also help to reduce the well-known effect of change 
blindness. (TO DO: cite paper here)

## Installation

Requirements:
* python 3 (tested with 3.9)
  
Set up a python environment and run `pip install -r requirements.txt`.

## Usage

`python pocc.py [-h] [-p P] [--nodata NODATA] [--startcolumn STARTCOLUMN] [--keys KEYS [KEYS ...]] [--vkey VKEY] filename classes`

with
* h: show a help message
* filename: path to a csv file with the data
* classes: the number of target classes.
* P: the factor to mark a change significant (TO DO: needs better explanation)
* NODATA: the value of missing data fields. These will be ignored.
* startcolumn: csv only. the column (zero-indexed) in which the timeseries data starts. All columns to the right will be treated as data.
* keys: geojson only. Name of the properties elements that contain data values. E.g. `--keys 2005 2010 2015`
* vkey: geojson only. Name of the properties element that contains a list of data. E.g. `--vkey data` when your geojson contains properties like "data": ["533.9","494.4","516.5","531.2"]

For example, if you want to classify the sample data into 4 classes, run:

`python main.py data/sampledata_cars_2005-2020.csv 4 --startcolumn 4` 

or

`python pocc.py data/sampledata_cars_2005-2020.geojson 4 --vkey data` 

or

`python pocc.py data/sampledata_cars_2005-2020_b.geojson 4 --keys 2005 2010 2015 2020` 

## To do / limitations:

* show POCC value for equidistant classifier
* include min+max intervall boundaries for class breaks (for easier colour ramps)
* visualise the output of geojson as PNGs