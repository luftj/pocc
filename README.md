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

`python main.py [-h] [-p P] [--nodata NODATA] filename startcolumn classes`

with
* filename: path to a csv file with the data
* startcolumn: the column (zero-indexed) in which the timeseries data starts. All columns to the right will be treated as data.
* classes: the number of target classes.
* P: the factor to mark a change significant (TO DO: needs better explanation)
* NODATA: the value of missing data fields. These will be ignored.

For example, if you want to classify the sample data into 4 classes, run:

`python main.py data/data_2005-2020.csv 2 4`

## To do / limitations:

* weighting not yet implemented