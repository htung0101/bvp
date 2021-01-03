# bvp

The B.lender V.ision P.roject (bvp) is a framework for creating visual stimuli using Blender. 

bvp consists of a library of python classes and functions, as well as a library of "scene elements" (objects, backgrounds, skies/lighting setups, shadows, and cameras) stored in .blend files and accessible through a database.

Scene elements are all managed by classes that wrap functionality of native Blender objects and store meta-data about each element (for example, the semantic category or size of an object). Each individual scene element is stored in a archival .blend files, and managed by a database system based on mongodb (http://www.mongodb.com/).

Scene elements can be combined using a Scene class, which has methods to populate a given scene with objects in random locations, render the scene, and more.

All relevant information for a set of scenes is stored in the SceneList 
class, which has methods for permanent storage / write-out of stimulus lists to archival files*. 

*Still to come 2017.03

# Installation

The INTENT with all this is to package all this code / all these dependencies as pip / conda packages. 

## Dependencies - non python:
* couchdb server (binaries avialable for unix, osx, and windows [here]()

## Dependencies - python 3.X (X depends on your version of blender):
* numpy 
* matplotlib 
* scipy
* pymongo

## Process
1) Download Blender (2.76 or later) [here](http://www.blender.org/)
	* For MacOS: delete `<path_to_blender_app>/blender.app/Contents/Resources/2.72/python` ... and all its sub-folders.
	* NOTE: capitalization of words in that path may vary with operating system / Blender version
	* Linux: 
	* Windows: Good luck & Godspeed to you, brave soul.
2) Make sure you have python3.X environment on your computer somewhere. Currently (2017.03) this should be 3.5. 

    * conda create -n py34 python=3.4 -c conda-forge pip==19
    * remove old pip (bin/pip and pip folder)
    * and run 
    * curl https://bootstrap.pypa.io/3.4/get-pip.py | python
	* I recommend you install this (and all your python packages) via anaconda: `sudo conda create -n py35 python=3.5 anaconda`  # creates python 3.5 environment with standard anaconda packages (numpy, scipy, matplotlib, more)
    * `sudo conda install -n py35 couchdb` # install couchdb
	* Once you have a python 3.4 environment somewhere add the following line to your ~/.bashrc or ~/.bash_profile file:
    * `export BLENDER_SYSTEM_PYTHON="<my_python3.X_path>"` (
    * For me (OSX version 10.11), the command is: `export BLENDER_SYSTEM_PYTHON="/Users/mark/anaconda/envs/py34/"`
3) Install couchdb server. 
    * See http://docs.mongodb.org/manual/installation/
    * Recommended install location is `~/mongodb/`

wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt-get install -y mongodb-org

4) Get BVP from github: `git clone https://github.com/marklescroart/bvp <your_bvp_path>`
	* `<your_bvp_path>` should be something like `~/Code/bvp`, or wherever you like keeping code
    * `cd <your_bvp_path>`
    * call `sudo python setup.py install` (OR, depending on your permissions on the system, `python setup.py install --user`)
    * You may have to replace `python` with `python3` or `python3.5` (etc) if you have multiple python installations and `python` does not point to the python3 version that is compatible with blender's python version
5) Set up config file [WIP!!] 


### At this point, BVP *should* be functional, but you won't have the ability to access / store things in a database without mongod installed & running


## Installation - Recommended

8) Set a blender alias -*-
    * add the following line to your ~/.bashrc or ~/.bash_profile file:
        - `alias blender="<path_to_blender>"`
    * Note that path_to_blender should be a path to the actual executable file, INSIDE the blender.app bundle, e.g.:
        - `alias blender="/Applications/blender.app/Contents/MacOS/blender"` # or wherever you installed blender.


# Contributing models to BVP

First: I love you for even reading this! 

If you have models in non-Blender form (3DS max, Sketchup, .off, whatever), and don't want to be bothered, EMAIL ME and we can talk. I love more models. I always want more models. 

If you are willing to actually putting them in BVP format, GREAT, we have tools for that. 

 
# Adding labels

The objects in the database are already labeled with semantic categories from the WordNet hierarchy. To add additional labels through the BVP blender addon GUI, you will need to make sure your system has the WordNet corpus downloaded for nltk (the Natural Language ToolKit for python)

# Links 
* What is a [.bashrc file](http://unix.stackexchange.com/questions/129143/what-is-the-purpose-of-bashrc-and-how-does-it-work)?
* What is the [difference between .bashrc and .bash_profile]()?
* What is a [PYTHONPATH](http://stackoverflow.com/questions/19917492/how-to-use-pythonpath)?
* Where do I find my [system python](https://wiki.python.org/moin/BeginnersGuide/Download)?
* Where can I find some [good](http://www.blenderguru.com/) [Blender](http://www.blender.org/support/tutorials/) [tutorials](https://cgcookie.com/learn-blender/)? 
* Why is this all so [DAMN COMPLICATED?](http://giphy.com/gifs/tantrum-sad-baby-13AXYJh2jDt2IE)