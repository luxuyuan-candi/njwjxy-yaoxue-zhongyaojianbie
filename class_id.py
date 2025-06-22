from source.load_dataset import Local_dataset
import os
import json

def main():
    # get dataset
    val_data_path = os.getcwd() + '/data/val'
    val_dataset = Local_dataset(val_data_path).get_dataset()
    transformer = {}
    for k,v  in  val_dataset.class_to_idx.items():
        transformer[v] = k
    with open('model/class.json', 'w', encoding='utf-8') as f:
        json.dump(transformer, f, ensure_ascii=False)
    

if __name__ == '__main__':
    main()