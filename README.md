# auto_ilp_759U
ENEE759U Final Project 
with Dr. Cunxi Yu
====================================

Setup Information 
====================================
  - Python3 is required
      - For Needed Packages Run:
        ```shell
        pip install networkx
        pip install argparse
        ```
To Set up the environment, run:
  In Linux Environment:
  ```shell
    # Shouldn't need to download, it is included in the repo
    wget http://ftp.gnu.org/gnu/glpk/glpk-5.0.tar.gz; tar -zxvf glpk-5.0.tar.gz
    sudo apt-get install build-essential
    # Run from here:
    cd glpk-5.0;./configure
    cd glpk-5.0; make
    cd ..
    # Run this if you start from scratch:
    git clone https://github.com/Yu-Maryland/ENEE759U.git
  ```
  Then, download and import auto_schedule.py to the main directory to run.

How to Run 
====================================
From the main directory (ENEE759U_final_project), run:
  ```shell
  python3 auto_schedule.py -h (or) --help
 ```
Example1: 
  To run minimum memory, latency constraint of 8 and area constraint of 4 on rand_DF_s10_1.edgelist:
  ```shell
  python3 auto_scheudle.py -f rand_DF_s10_1.edgelist -a 4 -ml 106
  ```

Example2: 
  Similarly, to run minimum latency, memory constraint of 150 and area constraint of 4 on rand_DF_s10_1.edgelist:
  ```shell
  python3 auto_scheudle.py -f rand_DF_s10_1.edgelist -a 4 -ll 150
  ```
