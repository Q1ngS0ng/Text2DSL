import csv

# Open the CSV file
# csv_path = './dataset/sls_log_type.csv'
csv_path = 'dataset/sls_log_type.CSV'
with open(csv_path, 'r', encoding='utf-8') as file:
    # Create a CSV reader object
    reader = csv.reader(file)

    # Iterate over each row in the CSV file
    for row in reader:
        # Print the key and value
        print(row)
        
    