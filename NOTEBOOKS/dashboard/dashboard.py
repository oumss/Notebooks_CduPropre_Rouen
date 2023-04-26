
# Les données d'exemple que l'on utilise si on n'a pas de points
samples = pd.DataFrame([
    np.asarray([48.822507, 2.268754]) + np.random.randn(2) * 0.004 for _ in range(50)
], columns=['lat', 'lon'])

# Les points où se trouvent les déchets
if "points" not in st.session_state:
    points = pd.DataFrame([], columns=['lat', 'lon'])
else:
    points = pd.DataFrame.from_dict(st.session_state["points"])
    
st.set_page_config(layout="wide", page_title="Détection de déchets")
st.write("## Détection de déchets")
tab_predict, tab_map = st.tabs(["Détection", "Map"])
tab_predict.write(
    "Vous pouvez charger n'importe quelle image afin de détecter les déchets sur celle-ci. Pour cela, veuillez charger une image dans le menu de gauche."
)

heatmap = tab_map.checkbox("Afficher la heatmap ?", value=True)
use_samples = tab_map.checkbox("Utiliser les données d'exemple ?", value=False)

tab_map.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=48.822507,
        longitude=2.268754,
        zoom=14
    ),
	layers=[
	    pdk.Layer(
	        'HeatmapLayer',
	        data=samples if use_samples else points,
	        get_position='[lon, lat]'
	    )
	    if heatmap else
	    pdk.Layer(
	        'ColumnLayer',
	        data=samples if use_samples else points,
	        get_position='[lon, lat]',
            radius=20,
            elevationScale=0,
            get_color="[255, 0, 0, 255]"
	    )
	]
))


# Download the fixed image
def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im


def detect(upload):
    image = Image.open(upload)
    col1.write("Image d'origine :camera:")
    col1.image(image)
    
    files = {'file':  convert_image(image)}
    response = requests.post(API_URL_PREDICT, files=files)
    predictions = json.loads(response.content)
    
    # Image avec les prédictions
    draw = ImageDraw.Draw(image, "RGBA")
    img_fraction = image.size[1] / 3200
    font = ImageFont.truetype("arial.ttf", int(max(15, 60 * img_fraction)))
    for p in predictions:
    	x, y, w, h, proba = p[1]
    	# TODO : Dessiner des rectangles sur l'images
    col2.write("Image avec les déchets détectés :wrench:")
    col2.image(image)
    return predictions

file_upload = tab_predict.file_uploader("Charger une image", type=["png", "jpg", "jpeg"])
col1, col2 = tab_predict.columns(2)

if file_upload is not None:
    predictions = detect(upload=file_upload)
    tab_predict.write("#### Résultats")
    for p in predictions:
        tab_predict.write("- **{}** (probabilité {:2.1f}%)".format(p[0], p[1][-1] * 100))
    tab_predict.write("#### Quelles sont les coordonnées de la photo ?")
    cols = tab_predict.columns(2)
    latitude = cols[0].number_input("Latitude", value=48.822507, min_value=0.0, max_value=90.0)
    longitude = cols[1].number_input("Longitude", value=2.268754, min_value=-180.0, max_value=180.0)
    validate_coords = tab_predict.button("Valider les coordonnées")

    if validate_coords:
        tab_predict.success("Image ajoutée dans la Map !")
        points = pd.concat((
            points,
            pd.DataFrame([[latitude, longitude]], columns=['lat', 'lon'])
        ), ignore_index=True)
        st.session_state["points"] = points.to_dict()

