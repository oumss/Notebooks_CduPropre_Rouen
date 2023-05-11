import torch

model = None

categories = ['Aluminium foil',
'Battery',
'Plastified paper bag',
'Aluminium blister pack',
'Other plastic bottle',
'Clear plastic bottle',
'Glass bottle',
'Plastic bottle cap',
'Metal bottle cap',
'Broken glass',
'Food Can',
'Aerosol',
'Drink can',
'Toilet tube',
'Other carton',
'Egg carton',
'Drink carton',
'Corrugated carton',
'Meal carton',
'Pizza box',
'Paper cup',
'Disposable plastic cup',
'Foam cup',
'Glass cup',
'Other plastic cup',
'Food waste',
'Glass jar',
'Plastic lid',
'Metal lid',
'Aluminium foil',
'Other plastic',
'Magazine paper',
'Tissues',
'Wrapping paper',
'Normal paper',
'Paper bag',
'Plastic film',
'Six pack rings',
'Garbage bag',
'Other plastic wrapper',
'Single-use carrier bag',
'Polypropylene bag',
'Crisp packet',
'Spread tub',
'Tupperware',
'Disposable food container',
'Foam food container',
'Other plastic container',
'Plastic glooves',
'Plastic utensils',
'Pop tab',
'Rope & strings',
'Scrap metal',
'Shoe',
'Squeezable tube',
'Plastic straw',
'Paper straw',
'Styrofoam piece',
'Unlabeled litter',
'Cigarette']

def load_model():
    global model
    model = torch.hub.load(
        'yolov5',
        'custom',
        path='./data/model.pt',
        source='local'
    )

def predict(image_path):
    global model
    predictions = model(image_path).xyxy
    if predictions is None or predictions is not None and len(predictions) == 0:
        return None

    predictions = predictions[0]
    result = []
    for p in predictions:
        category = categories[int(p[-1])]
        box = p[:-1]
        result.append((category, box.numpy().tolist()))
    return result
