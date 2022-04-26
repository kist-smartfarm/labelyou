# ~~labelme~~  labelyou
<img src="./labelme/icons/icon.png" width="200" height="200">
---
## Description 

labelyou is image annotation tool forked from [labelme](https://github.com/wkentaro/labelme) 

it is developed for supporting workflows in the KIST smartfarm research center. 

modified by : Hong-Beom Choi(redtiger@kist.re.kr)

## Features

* Including all features of the mother project, labelme. 
* Grid mode, which generates a bunch of rectangles in the form of cells in a grid. 
* Ergonomically modified keyboard shortchts, including changing class. 

## Installation 

Prepare the repository (!! on your workspace !!) 
```
git clone https://github.com/kist-smartfarm/labelyou
```

install requried packages
```
cd labelyou
conda create -n labelyou python=3.9 
conda activate labelyou
pip install . # if you want to modify this package -> pip install -e . 
```

run labelyou 
```
cd labelme
python __main__.py
```



