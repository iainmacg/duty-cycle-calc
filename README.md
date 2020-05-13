"# duty-cycle-calc"

Duty Cycle Calculator

User Guide

Iain MacGilp - June 2019


The Duty Cycle Calculator is a tool used to analyse batches of SEM (scanning electron microscopy) grating images. It works as a plugin within the Fiji (ImageJ) program by opening an image, plotting the intensity of a line scan, identifying the peaks, then calculating resultant duty cycle and recording the result.

Setup Instructions

1.	Download Fiji: https://imagej.net/Fiji/Downloads
2.	Add BAR update site to Fiji: https://imagej.net/BAR
3.	Install the plugin: Copy the .py file into the plugins folder within the Fiji installation directory
4.	Run: In the Plugins tab of Fiji, navigate to the bottom of the list and click on the Duty Cycle Calculator

User interface

Input image directory: select a directory to analyse images from. Subdirectories will be included.
Output results directory: select a directory to store the output files.
Scans per image: number of line scans per image. Scans will be evenly distributed across images.
File types: optional, specify file extensions to include. Multiple types can be separated using “;”.
Filter: optional, will only process images that contain this string in filename. Multiple strings can be separated using “;”.
Horizontal grating lines: check for SEMs of horizontal lines, uncheck for vertical lines. Examples shown below.

Limitations: currently, the method cannot differentiate between mark/space in SEM images – the duty is given based on whichever peak comes first in the image. Developed PMMA that is unsputtered does not provide enough contrast to measure. Low magnification/SEMs with many repeats are more prone to calculation errors. This tool is less suitable for cross sectional SEMs.
