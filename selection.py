
import csv 
from dm_evaluation import calculate_dm_signal
 




def additems():
    special_add_list = []
    with open(r'buff.csv',encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        
        items = list(csv_reader)

    n = 0 
    it_count =0 
   
    for item in items[0] :
            it_count+= 1
            
            
            dm_signal = calculate_dm_signal(item)
            

            if dm_signal :
                special_add_list.append(item)
    with open('items.csv', 'w', newline='') as file:
                    # Step 4: Using csv.writer to write the list to the CSV file
        writer = csv.writer(file)
        writer.writerow(special_add_list) # Use writerow for single list
additems()