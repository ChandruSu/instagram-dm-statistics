# Instagram Direct Message Analytics

Instagram direct message analyser reads downloadable user data and calculates and returns conversation statistics and plots graphs to represent analytics. Program is a python script which uses the Pandas library and the MatPlotLib module.

## Requirements

Before running the python script, the following prerequisites must be met:

1. Have python (version 3.10 or greater) installed on your system

2. Install the pip modules specified in the [requirements.txt](/requirements.txt) file to your system or in a python virtual environment

3. Download your instagram user data by logging in to your account and going to `Settings > Privacy and Security > Data download` and navigate to the inbox directory

## Running

To run the python script, activate the virtual machine if necessary, then execute the following command in a terminal:

```bash
python -path /path/to/dir --plot
```

### CLI Parameters

Script provides a very simple command line interface 

|Parameter|Description|
|---|---|
|`-path`|Allows user to specify path to inbox directory containing message.json files. Requires additional argument (path). By default, script searches message files in the same directory.|
|`--plot`|Plots matplotlib stacked bar chart displaying messages by user over time. |
|`--help`|Prints help text and terminates program prematurely.|