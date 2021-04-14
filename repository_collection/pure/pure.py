import rispy

filepath = "Pure_100321.ris" 
with open(filepath, 'r', encoding="utf8") as pure_data:
    entries = rispy.load(pure_data)
    for entry in entries:
        print(entry)