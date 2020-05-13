#@ File(label='Input image directory', style='directory') input_dir
#@ File(label='Output results directory', style='directory') output_dir
#@ String(label='Scans per image', value='3') input_scans
#@ String(label='File types', value='tif;jpeg') file_types
#@ String(label='Filter', value='') filters
#@ String(label='Exclusion Filter', value='') ex_filters
#@ Boolean(label='Horizontal grating lines', value=True) do_horizontal

'''Duty cycle calculator
Calculates grating duty cycle from SEM images

Script uses the Find Peaks tool from BAR (use Fiji to install)

Part of this code is borrowed from the Jython tutorial at the ImageJ wiki.
http://imagej.net/Jython_Scripting#A_batch_opener_using_os.walk.28.29
'''

from __future__ import division
import os
from java.io import File
from ij import IJ
from ij.process import ImageConverter
import sys
import csv
import operator
import datetime
from math import sqrt

if __name__ == '__main__':
    main()

start_time = datetime.datetime.now()
folder = str(start_time).split('.', 1)[0]
folder = folder.replace(":", "_")
IJ.log("-----------------------------------------------------------------------------------------------------------------")
IJ.log("Batch started " + str(start_time))
setting = "min._peak_amplitude=50 min._peak_distance=0.0015 min._value=190 max._value=0 exclude list"
IJ.log("BAR Find Peaks settings: " + setting)
results = [("Sample ID", "Filename", "Scan", "Duty 1", "Duty 2", "Scan stdev1", "Scan stdev2", "Peaks", "Max Duty", "Min Duty")]
csvpath = str(output_dir) + "\\Duty " + str(folder) + "\\"
os.mkdir(csvpath)
num_scans = int(input_scans)
num_scans += 1
IJ.log("Input image directory: " + str(input_dir))
IJ.log("Output results directory: " + str(csvpath))
IJ.log("Number of scans per image: " + str(input_scans))
IJ.log("File types: " + str(file_types))
IJ.log("Filters: " + str(filters))
IJ.log("Horizontal grating lines: " + str(do_horizontal))
IJ.selectWindow("Log")
IJ.saveAs("Text", csvpath + "Duty_Log.txt")

def sort_table(table, col=0):
    return sorted(table, key=operator.itemgetter(col))

def duty_cycle(i, horizontal):
	IJ.open(i)
	IJ.run("Enhance Contrast...", "saturated=0.3 equalize")
	IJ.run("Smooth", "")
	'IJ.run("Anisotropic Diffusion 2D", "number=20 smoothings=1 keep=20 a1=0.50 a2=0.90 dt=20 edge=5")     # use instead of smooth for better results, slower
	imp = IJ.getImage()
	ImageConverter(imp).convertToGray8()
	file_base = str(imp.title)								# convert name into string
	file_base = file_base.split('.', 1)[0]					# remove all characters including and after .
	sample_id = file_base.split('_', 1)[0]
	height = imp.height
	width = imp.width
	IJ.run(imp, "Set Scale...", "distance=5000 known=1 pixel=1 unit=cm")
	IJ.setTool("line")
	for scan in range(1, num_scans):
		row_count = 0
		data=[]
		data2=[]
		last = 0
		filename = file_base + "_" + str(scan)
		
		if not horizontal:
			IJ.makeLine(0, scan*height/num_scans, width, scan*height/num_scans)				# horizontal line to measure vertical grating profile		
		else:
			IJ.makeLine(width*scan/num_scans, 9*height/10, width*scan/num_scans, 0)			# vertical line to measure horizontal grating profile
		
		IJ.run(imp, "Plot Profile", "")
		imp_plot = IJ.getImage()
		IJ.run(imp, "Find Peaks", setting)	# nw07 params: min._peak_amplitude=60 min._peak_distance=0 min._value=100 max._value=0 exclude list
		IJ.saveAs("Results", csvpath + filename + "_raw.csv")
		imp_plot.close()
		imp_plot = IJ.getImage()
		IJ.saveAs("Png", csvpath + "Peaks in Plot of " + filename + ".png")
		imp_plot.close()
		IJ.selectWindow(filename + "_raw.csv")
		IJ.run("Close")
		
		with open(csvpath + filename + "_raw.csv", "rb") as fin, open(csvpath + filename + "_peaks.csv", "wb") as fout:  
		    writer = csv.writer(fout)            
		    for row in csv.reader(fin):
		        if not row[2] == '':
		             writer.writerow(row)

		with open(csvpath + filename + "_peaks.csv", "rb") as File:
		    reader = csv.reader(File)
		    for row in reader:
		        row_count += 1
			if row_count == 1:
				continue
			data.append(tuple(row))								# Append all non-header rows into a list of data as a tuple of cells
		for row in sort_table(data, 2):
			data2.append(tuple(row))
		if len(data2) < 3:
			IJ.log(filename + " no peaks detected, skipping...")
			continue
		else:
			peaks = len(data2)
			last = data2[0]
			last = last[2]
			
			row_count = 0
			diff = 0
			colG = []
			blank = ""
			duty = zip(*data2)
			for row in data2:
				row_count += 1
				if row_count == 1:
					continue
				else:
					print row[2]
					print last
					diff = float(row[2]) - float(last)
					colG.append(diff)
					last = row[2]
			a, b = colG[::2], colG[1::2]
			avga = sum(a)/len(a)
			avgb = sum(b)/len(b)
			a_len_dev = len(a) - 1
			b_len_dev = len(b) - 1
			if b_len_dev > 1:
				a_stdev = sqrt(sum((x - avga)**2 for x in a) / a_len_dev)
				b_stdev = sqrt(sum((x - avgb)**2 for x in b) / b_len_dev)
			else:
				a_stdev = 1
				b_stdev = 1
			
			duty_cyc = avga/(avga+avgb)
			perc = duty_cyc*100
			invperc = 100 - perc
			inv_duty = 1 - duty_cyc
			duty_max = max(duty_cyc, inv_duty)
			duty_min = min(duty_cyc, inv_duty)
			percs = round(perc)
			percs = int(percs)
			percs = str(percs)
			invpercs = round(invperc)
			invpercs = int(invpercs)
			invpercs = str(invpercs)
		
			colG.insert(0, blank)
			a.insert(0, blank)
			b.insert(0, blank)
			b.insert(1, blank)
			
			i = 0
			while i < len(a):
					i += 2
					a.insert(i, blank)
			
			i = 1
			while i < len(b):
					i += 2
					b.insert(i, blank)
			
			duty.append(colG)
			duty.append(a)
			duty.append(b)	
			duty = zip(*duty)
			result = [sample_id, file_base, scan, duty_cyc, inv_duty, a_stdev, b_stdev, peaks, duty_max, duty_min]
			header = ["X0", "Y0", "X1", "Y1", "X2", "Y2", "diff", "a", "b"]
			results.append(result)
			with open(csvpath + filename + "_duty.csv", 'wb') as myfile:
				wr = csv.writer(myfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
				wr.writerow(header)
				wr.writerows(duty)
			print(filename + " duty cycle is " + percs + "/" + invpercs + "%.")
			IJ.log(filename + " duty cycle is " + percs + "/" + invpercs + "% (" + str(peaks) + " peaks found)")
			with open(csvpath + "results.csv", 'wb') as myfile:
				wr = csv.writer(myfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
				wr.writerows(results)		# Write the result data from all images into a single csv file

def batch_open_images(path, file_type=None, name_filter=None, horizontal=False):
    '''Open all files in the given folder.
    :param path: The path from were to open the images. String and java.io.File are allowed.
    :param file_type: Only accept files with the given extension (default: None).
    :param name_filter: Only accept files that contain the given string (default: None).
    '''
    # Converting a File object to a string.
    if isinstance(path, File):
        path = path.getAbsolutePath()

    def check_type(string):
        '''This function is used to check the file type.
        It is possible to use a single string or a list/tuple of strings as filter.
        This function can access the variables of the surrounding function.
        :param string: The filename to perform the check on.
        '''
        if file_type:
            # The first branch is used if file_type is a list or a tuple.
            if isinstance(file_type, (list, tuple)):
                for file_type_ in file_type:
                    if string.endswith(file_type_):
                        # Exit the function with True.
                        return True
                    else:
                        # Next iteration of the for loop.
                        continue
            # The second branch is used if file_type is a string.
            elif isinstance(file_type, string):
                if string.endswith(file_type):
                    return True
                else:
                    return False
            return False
        # Accept all files if file_type is None.
        else:
            return True

    def check_filter(string):
        '''This function is used to check for a given filter.
        It is possible to use a single string or a list/tuple of strings as filter.
        This function can access the variables of the surrounding function.
        :param string: The filename to perform the filtering on.
        '''
        if name_filter:
            # The first branch is used if name_filter is a list or a tuple.
            if isinstance(name_filter, (list, tuple)):
                for name_filter_ in name_filter:
                    if name_filter_ in string:
                        # Exit the function with True.
                        return True
                    else:
                        # Next iteration of the for loop.
                        continue
            # The second branch is used if name_filter is a string.
            elif isinstance(name_filter, string):
                if name_filter in string:
                    return True
                else:
                    return False
            return False
        else:
        # Accept all files if name_filter is None.
            return True

    # We collect all files to open in a list.
    path_to_images = []
    # Replacing some abbreviations (e.g. $HOME on Linux).
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)

    # os.walk() is iterable.
    # Each iteration of the for loop processes a different directory.
    # the first return value represents the current directory.
    # The second return value is a list of included directories.
    # The third return value is a list of included files.
    for directory, dir_names, file_names in os.walk(path):
        # We are only interested in files.
        file_names = [f for f in file_names if not f[0] == '.']
        file_names = [f for f in file_names if str(ex_filters) not in f]
        for file_name in file_names:
            # The list contains only the file names.
            # The full path needs to be reconstructed.
            full_path = os.path.join(directory, file_name)
            # Both checks are performed to filter the files.
            if check_type(file_name):
                if check_filter(file_name):
                    # Add the file to the list of images to open.
                    path_to_images.append(full_path)
    # Create the list that will be returned by this function.
    images = []
    for img_path in path_to_images:
        # IJ.openImage() returns an ImagePlus object or None.
        i = IJ.openImage(img_path)
        duty_cycle(img_path, horizontal)
        IJ.selectWindow("Log")
        IJ.saveAs("Text", csvpath + "Duty_Log.txt")
        IJ.run("Close All", "")
        # An object equals True and None equals False.
        if i:
            images.append(i)
    return images

def split_string(input_string):
    '''Split a string to a list and strip it
    :param input_string: A string that contains semicolons as separators.
    '''
    string_splitted = input_string.split(';')
    # Remove whitespace at the beginning and end of each string
    strings_striped = [string.strip() for string in string_splitted]
    return strings_striped

if __name__ in ['__builtin__','__main__']:
    # Run the batch_open_images() function using the Scripting Parameters.
    images = batch_open_images(input_dir,
                               split_string(file_types),
                               split_string(filters),
                               do_horizontal
                              )
    for image in images:
        # Call the toString() method of each ImagePlus object.
        print(image)
with open(csvpath + "results.csv", 'wb') as myfile:
	wr = csv.writer(myfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	wr.writerows(results)		# Write the result data from all images into a single csv file
end_time = datetime.datetime.now()
IJ.log("Batch ended " + str(end_time))
IJ.selectWindow("Log")
IJ.saveAs("Text", csvpath + "Duty_Log.txt")
