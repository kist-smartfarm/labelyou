import PIL 
import pathlib 
from multiprocessing import Pool
import json 
import datetime
from .grid import to_excel

def get_annotation_file_list(image_list): 
    json_list = [] 
    for _path in image_list: 
        json_path = pathlib.Path(_path).with_suffix('.json') 
        if pathlib.Path.exists(json_path): 
            json_list.append(json_path)
    return json_list
     
def export_workspace_images(image_list): 
    json_list = get_annotation_file_list(image_list)
    for json_file in json_list: 
        with open(json_file) as f: 
            data = json.load(f) 

            image_name = data['imagePath']
            
            img = PIL.Image.open(str(json_file.parents[0] / image_name))
            output_dir = json_file.parents[0] / f'{str(pathlib.Path(image_name).with_suffix(""))}'
            output_dir.mkdir(exist_ok=True, parents=True)

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
                cropped_img_path = output_dir / cropped_img_name
                cropped_img.save(cropped_img_path)
            

def export_workspace_annotation_report(image_list): 
    json_list = get_annotation_file_list(image_list)
    print(json_list)
