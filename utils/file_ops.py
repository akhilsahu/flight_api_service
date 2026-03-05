

def write_to_file(data,filename="./uploads/data.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(data)