import PIL 
import pathlib 
from multiprocessing import Pool
import json 
import datetime
from .grid import to_excel
import csv

def get_annotation_file_list(image_list): 
    json_list = [] 
    for _path in image_list: 
        json_path = pathlib.Path(_path).with_suffix('.json') 
        if pathlib.Path.exists(json_path): 
            json_list.append(json_path)
    return json_list
     
def export_workspace_images(image_list): 
    json_list = get_annotation_file_list(image_list)
    output_dir = 'annotations_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    for json_file in json_list: 
        with open(json_file) as f: 
            data = json.load(f) 

            image_name = data['imagePath']
            
            img = PIL.Image.open(str(json_file.parents[0] / image_name))
            output_sub_dir = json_file.parents[0] / output_dir 
            output_sub_dir = output_sub_dir / f'{str(pathlib.Path(image_name).with_suffix(""))}'
            output_sub_dir.mkdir(exist_ok=True, parents=True)

            for i, shape in enumerate(data['shapes']): 
                if shape['shape_type'] != 'rectangle': 
                    continue
                left = min(shape['points'][0][0], shape['points'][1][0]) 
                right = max(shape['points'][0][0], shape['points'][1][0]) 
                bottom = max(shape['points'][0][1], shape['points'][1][1]) 
                top = min(shape['points'][0][1], shape['points'][1][1]) 
                cropped_img = img.crop((left, top, right, bottom))

                cropped_img_name = f"{shape['label']}.png"
                if 'grid_x' in shape and 'grid_y' in shape:
                    cropped_img_name = "_".join([str(i),
                        shape['group_id'] if shape['group_id'] else "",
                        to_excel(shape['grid_x']+1) + str(shape['grid_y']+1),
                        cropped_img_name])
                else: 
                    cropped_img_name = "_".join([str(i), cropped_img_name])
                cropped_img_path = output_sub_dir / cropped_img_name
                cropped_img.save(cropped_img_path)
            

def export_workspace_label_report(image_list): 
    json_list = get_annotation_file_list(image_list)
    if len(json_list) == 0: 
        return
    export_records = [] 
    for json_file in json_list: 
        with open(json_file) as f: 
            data = json.load(f)
            filename = data['imagePath']
            if len(data['shapes']) > 0: 
                for annotation_id, shape in enumerate(data['shapes']): 
                    annotation_type = shape['shape_type']
                    label = shape['label']
                    group_id = shape['group_id']
                    grid_x = shape['grid_x'] + 1 if 'grid_x' in shape else ""
                    grid_y = shape['grid_y'] + 1 if 'grid_y' in shape else ""
                    
                    export_records.append([
                        filename, 
                        annotation_id, 
                        annotation_type,
                        group_id if group_id else "", 
                        label,
                        to_excel(grid_x) + str(grid_y) if grid_x and grid_y else "", 
                        grid_x,
                        grid_y
                    ])
                
                output_filename = json_list[0].parents[0] / ('label_report_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) 
                with open(output_filename.with_suffix(".csv"),'w',newline='') as f:
                    wr = csv.writer(f) 
                    wr.writerow(["filename", "index", "annotation_type", "group_id", "label", "xy", "x", "y"])
                    for record_per_file in export_records: 
                        wr.writerow(record_per_file)
  

def export_workspace_flag_report(image_list): 
    json_list = get_annotation_file_list(image_list)
    if len(json_list) == 0: 
        return
    jsons = []
    flag_set = set()
    export_records = [] 
    for json_file in json_list: 
        with open(json_file) as f: 
            data = json.load(f)
            jsons.append(data) 
            flag_set.update(data['flags'].keys()) 

    flag_list = list(flag_set)
    flag_list.sort() 
    
    for j in jsons: 
        record = []
        record.append(j['imagePath'])
        for flag in flag_list: 
            record.append(j['flags'][flag] if flag in j['flags'] else False) 
        export_records.append(record)
       
    output_filename = json_list[0].parents[0] / ('flag_report_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) 
    with open(output_filename.with_suffix(".csv"),'w',newline='') as f:
        wr = csv.writer(f) 
        wr.writerow(["filename"] + flag_list)
        for record_per_file in export_records: 
            wr.writerow(record_per_file)
