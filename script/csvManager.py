import csv
import os

def results_to_csv(results, headers: list[str], folder: str):
    csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder + "/final_results.csv")
    csv_file = os.path.normpath(csv_file) # normalize path separators
    csv_folder = os.path.dirname(csv_file)
    
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)

    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(results)