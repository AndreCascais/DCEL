# DCEL

DCEL implementation to allow horizontal and grid partition of orthogonal polygons.

## Usage

### Packages

In order to run the program it is necessary to install bintrees and numpy packages

### How to run
The program should be run as follows

`python2 Test.py`

the user can then choose an input file from the sampledatafolder

### Available flags

The flags should be added in the first line of the provided examples

- 0 - horizontal partiton
- 1 - grid partition
- 2 - grind partition and visualisation matrix (this will print the necessary data for GLPK)

Note: flag 2 may take a while to finish

## Available commands

- q - quit
- h - print help message
- p - print dcel

- e - iterate through next hedges
- b - iterate through previous hedges
- t - iterate through twins
- v - iterate through vertices
- f - iterate through faces
