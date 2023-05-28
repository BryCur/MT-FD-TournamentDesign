import colorsys
import pandas as pd
import numpy as np
import os
import csv
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.stats import norm


# simId,kendalTauDistance,disagreement,matchCount,tieCount,completeDuplicateMatches

plt.style.use('_mpl-gallery')
mpl.rcParams['font.size'] = 17
mpl.rcParams['lines.linewidth'] = 3
mpl.rcParams['figure.subplot.left'] = 0.07  # Set default left padding
mpl.rcParams['figure.subplot.bottom'] = 0.07  # Set default bottom padding


def map_filename_to_color(filename:str):
    # Extract the number and type from the filename
    parts = filename.split("-")
    number = int(parts[0][:2])
    file_type = parts[1]

    # Define the colors for each file type
    colors = {
        "RoundRobin": "#0b16b5", # blue
        "SingleKnockout": "#b50b0b", # red
        "SwissSystem": "#0bb51c", # green
        "RR": "#0b16b5", # blue
        "SK": "#b50b0b", # red
        "SS": "#0bb51c", # green
        "Custom": "#b57c0b" # orange
    }

    # Determine the saturation based on the number
    saturation = min(number / 81 * 1.5, 1)

    # Determine the color based on the file type
    hue = colors.get(file_type, "#000000")

    # Convert the color to HSV and adjust the saturation
    r, g, b = tuple(int(hue[i:i+2], 16) for i in (1, 3, 5))
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    s = saturation
    r, g, b = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))

    # Convert the color back to HEX and return it
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def drawBoxplotFromFilesInFolderForColumn(relative_root_folder_path: str, colName: str):
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_root_folder_path))
    name_list = []
    data_list = []
    color_list = []
    this_plot = plt

    for filename in os.listdir(root):
        if filename.endswith('.csv'): # if csv file then we process it
            path = relative_root_folder_path + filename
            parts = filename.split("-")
            data = pd.read_csv(path)[colName]
            name_list.append(f"{parts[1][:-4]} - {parts[0][:-1]} teams")
            data_list.append(list(data))
            color_list.append(map_filename_to_color(filename[:-4]))

    this_plot.title("KTRC measures per format and size")

    # Sort the handles and labels alphabetically

    this_plot.ylabel('Kendall Tau Rank Correlation')
    this_plot.xlabel('Format and size')        
    mpl.rcParams['figure.subplot.right'] = 0.85

    sorted_data = sorted(zip(name_list, data_list, color_list))
    name_list, data_list, color_list = zip(*sorted_data)

    for i, box in enumerate(this_plot.boxplot(data_list, labels=name_list, patch_artist=True, meanline=True, showmeans=True)['boxes']):
        box.set_facecolor(color_list[i])
    return(plt.show())


# drawBoxplotFromfilesForColumn(['9t-Round-Robin.csv','9t-SingleKnockout.csv', '9t-SwissSystem.csv'], 'kendalTauDistance')

# plt.plot(roundsPlayed, meanKDTC, KTDC_sd)
# plt.show()


def plotForCustom():
    folder= f"./simulations/custom-18-teams/"
    csv_name_list = ["18custom-RoundRobin.csv", "18custom-SwissSystem.csv"]
    colName = "kendalTauDistance"
    name_list = []
    data_list = []
    color_list = []

    this_plot= plt

    for name in csv_name_list:
        path = folder + name
        dataframe = pd.read_csv(path)
        name_list.append(f"{name[9:-4]}-{dataframe['matchCount'][0]}matches")
        data_list.append(list(dataframe[colName]))
        color_list.append(map_filename_to_color(name[:-4]))
        
    this_plot.ylabel('Kendall Tau Rank Correlation')
    this_plot.xlabel('Format and size') 

    for i, box in enumerate(this_plot.boxplot(data_list, labels=name_list, patch_artist=True, meanline=True, showmeans=True)['boxes']):
        box.set_facecolor(color_list[i])
        
        #plt.boxplot(data_list, labels=name_list)
    return(this_plot.show())

def cumulativeAverageForCustom():
    folder= f"./simulations/test/"
    csv_name_list = ["18custom-RoundRobin.csv", "18custom-SwissSystem.csv"]
    colName = "kendalTauDistance"
    name_list = []
    data_list = []
    for name in csv_name_list:
        path = folder + name
        dataframe = pd.read_csv(path)[colName]
        avgs: list[float] = []
        sum = 0
        for data in dataframe:
            sum += data
            avgs.append(sum / (len(avgs)+1))
        name_list.append(name[:-4])
        data_list.append(avgs)
        
    plt.plot(data_list[0])
    plt.plot(data_list[1])
    return(plt.show())


def cumulativeAverageForAllFile(relative_root_folder_path: str, colName: str):
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_root_folder_path))
    this_plot = plt

    # iterate through all files in folder
    for filename in os.listdir(root):
        if filename.endswith('.csv'): # if csv file then we process it
            path = relative_root_folder_path + filename
            dataframe = pd.read_csv(path)[colName]
            avgs: list[float] = []
            sum = 0

            parts = filename.split("-")

            for data in dataframe: # compute the cumulative average for file
                sum += data
                avgs.append(sum / (len(avgs)+1))

            this_plot.plot(avgs, label=f"{parts[1][:-4]} - {parts[0][:-1]} teams", color=map_filename_to_color(filename[:-4]))
        

    # Get the handles and labels for the plot
    handles, labels = this_plot.gca().get_legend_handles_labels()

    # Sort the handles and labels alphabetically
    sorted_labels, sorted_handles = zip(*sorted(zip(labels, handles)))
    this_plot.legend(sorted_handles, sorted_labels, loc="upper right", bbox_to_anchor=(1.2, 1))

    this_plot.ylabel('K. Tau Rank Correlation')
    this_plot.xlabel('Repetition')
    return this_plot.show()

def printStuffForAllFile(relative_root_folder_path: str, colName: str):
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_root_folder_path))

    average_list = []
    std_dev_list = []
    confidence_interval_list = []
    print("file,colName,avg,sd,cilowerbound,ciupperbound,matchcount")
    # iterate through all files in folder
    for filename in os.listdir(root):
        if filename.endswith('.csv'): # if csv file then we process it
            path = relative_root_folder_path + filename
            dataframe = pd.read_csv(path)

            # Calculate statistics
            average = dataframe[colName].mean()
            std_dev = dataframe[colName].std()
            matchCnt = dataframe["matchCount"]
            confidence_interval_width = 1.96 * std_dev / np.sqrt(len(dataframe))  # Assuming 95% confidence interval

            lower_bound, upoper_bound = (average - confidence_interval_width, average+confidence_interval_width)


            average_list.append(average)
            std_dev_list.append(std_dev)
            confidence_interval_list.append(confidence_interval_width)

            parts = filename.split("-")

            print(f"{filename[:-4]},{colName},{average},{std_dev},{lower_bound},{upoper_bound},{matchCnt[0]}")



def get_sk_winner_check_stat(): 
    relative_root_folder_path = "simulations/SingleKnockoutExperiment/"
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_root_folder_path))
    this_plot = plt

    average_list = []
    std_dev_list = []
    confidence_interval_list = []
    name_list = []
    print("format,teamCount,ktrcavg,ktrcsd,cilowerbound,ciupperbound,matchcount")
    # iterate through all files in folder
    for filename in os.listdir(root):
        if filename.endswith('.csv'): # if csv file then we process it
            path = relative_root_folder_path + filename
            dataframe = pd.read_csv(path)["kendalTauDistance"]

            # Calculate statistics
            average = dataframe.mean()
            std_dev = dataframe.std()
            confidence_interval_width = 1.96 * std_dev / np.sqrt(len(dataframe))  # Assuming 95% confidence interval

            lower_bound, upoper_bound = (average - confidence_interval_width, average+confidence_interval_width)


            average_list.append(average)
            std_dev_list.append(std_dev)
            confidence_interval_list.append(confidence_interval_width)

            print(f"{filename} - {average*100}")

def get_rr_stat(): 
    relative_root_folder_path = "simulations/Roundrobin_obs/result.csv"
    dataframe = pd.read_csv(relative_root_folder_path)
    this_plot = plt

    xAxis = dataframe["participantCnt"]
    values = dataframe["ktrcavg"]

    # Sort the handles and labels alphabetically

    this_plot.ylabel('Kendall Tau Rank Correlation score')
    this_plot.xlabel('# of participants in Round-Robin') 

    for i, val in enumerate(values):
        this_plot.annotate(f"{dataframe.matchcount[i]} matches", (xAxis[i], val), textcoords="offset points", xytext=(0,10), ha='center')


    this_plot.plot(xAxis, values)
    this_plot.show()

def get_ss_stat(): 
    relative_root_folder_path_12t = "simulations/SwissSystem_obs/12-teams/result.csv"
    relative_root_folder_path_9t = "simulations/SwissSystem_obs/9-teams/result.csv"
    relative_root_folder_path_6t = "simulations/SwissSystem_obs/6-teams/result.csv"


    dataframe = pd.read_csv(relative_root_folder_path_6t)
    this_plot = plt

    xAxis = dataframe["roundCnt"]

    values_6t = dataframe["ktrcavg"]
    for i, val in enumerate(values_6t):
        this_plot.annotate(f"{dataframe.matchcount[i]} matches", (xAxis[i], val), textcoords="offset points", xytext=(10,10), ha='center')

    #label=f"{parts[1][:-4]} - {parts[0][:-1]} teams", color=map_filename_to_color(filename[:-4])
    this_plot.plot(xAxis, values_6t, label="SS - 6 Teams")

    # =====================================

    dataframe = pd.read_csv(relative_root_folder_path_9t)
    values_9t = dataframe["ktrcavg"]

    for i, val in enumerate(values_9t):
        this_plot.annotate(f"{dataframe.matchcount[i]} matches", (xAxis[i], val), textcoords="offset points", xytext=(10,10), ha='center')

    #label=f"{parts[1][:-4]} - {parts[0][:-1]} teams", color=map_filename_to_color(filename[:-4])
    this_plot.plot(xAxis, values_9t, label="SS - 9 Teams")

        # =====================================

    dataframe = pd.read_csv(relative_root_folder_path_12t)
    values_12t = dataframe["ktrcavg"]

    for i, val in enumerate(values_12t):
        this_plot.annotate(f"{dataframe.matchcount[i]} matches", (xAxis[i], val), textcoords="offset points", xytext=(10,-20), ha='center')

    #label=f"{parts[1][:-4]} - {parts[0][:-1]} teams", color=map_filename_to_color(filename[:-4])
    this_plot.plot(xAxis, values_12t, label="SS - 12 Teams")

    this_plot.ylabel('Kendall Tau Rank Correlation score')
    this_plot.xlabel('# of rounds played') 
    this_plot.legend(loc="upper right", bbox_to_anchor=(1.2, 1))
    this_plot.show()

#get_ss_stat()
#get_sk_winner_check_stat()
#printStuffForAllFile("simulations/SwissSystem_obs/12-teams/", "kendalTauDistance")

#drawBoxplotFromFilesInFolderForColumn("simulations/Observation_batch/", "kendalTauDistance")
cumulativeAverageForAllFile("simulations/Observation_batch/", "kendalTauDistance")

#printStuffForAllFile("simulations/custom-18-teams/", "completeDuplicateMatches")
#plotForCustom()