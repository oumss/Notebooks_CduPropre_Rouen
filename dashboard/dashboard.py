from streamlit.components.v1 import html
from PIL import Image, ImageDraw, ImageFont, ImageColor 
from io import BytesIO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pydeck as pdk
import requests 
import json 
import colorsys
import time
from matplotlib.patches import Polygon, Rectangle 
import altair as alt
from urllib.error import URLError


API_URL_PREDICT = "http://localhost:8080//predict"

#py -m streamlit run dashboard.py


# Warmup 
requests.get(API_URL_PREDICT)
np.random.seed(0)

#[theme]
primaryColor="#ACC687"
backgroundColor="#F4F4F4"
secondaryBackgroundColor="#D9D9D9"
textColor="#737373"
font="arial.ttf"


# Les données d'exemple que l'on utilise si on n'a pas de points
samples = pd.DataFrame([
    np.asarray([48.822507, 2.268754]) + np.random.randn(2) * 0.004 for _ in range(50)
], columns=['lat', 'lon'])
data = np.array([[48.822507, 2.268754],[48.8225507, 2.261754],[48.822547, 2.268764],[48.822247, 2.268564]])

# Les points où se trouvent les déchets
if "points" not in st.session_state:
    points = pd.DataFrame(data, columns=['lat', 'lon'])
else:
    points = pd.DataFrame.from_dict(st.session_state["points"])
    
st.set_page_config(layout="wide", 
                   page_title="Dashboard CduPropre", 
                   initial_sidebar_state="expanded",
                  )

st.write("# Dashboard : CduPropre Rouen ")
st.write("Sur ce dashboard vous pouvez détécter des déchets sur vos propre images grâce à notre modèle, de plus vous pouvez alimenter notre base de données en indiquant les coordonnées de l'image, vous avez accès à une map vous montrant tous les déchets présents dans notre base, de quelques statistiques sur les déchets dans les villes de France et enfin une présentation de nous même et de notre application mobile ! ")
tab_stats, tab_predict, tab_map, tab_us, tab_app = st.tabs(["📈 Statistiques", "📷 Détection", "🗺️ Map", "😎 Qui sommes nous ?", "📱 CduPropre Application"])

### Sidebar ###
st.sidebar.write("# CduPropre Rouen")
image = Image.open('../logo/logo_cote.png')
st.sidebar.image(image, width=180)
st.sidebar.write("### Localisation : Rouen")
st.sidebar.write("Déchets comptabilisés : 19 876")
st.sidebar.write("Déchets ramassés : 5 875")

### Prédiction ###
tab_predict.write(
    "Vous pouvez charger n'importe quelle image afin de détecter les déchets sur celle-ci. Pour cela, veuillez charger une image dans le menu de gauche."
)



### Statistiques ###
tab_stats.write("Quelques statistiques calculés concernant les déchets dans les villes")

@st.cache_data
def get_UN_data():
    AWS_BUCKET_URL = "https://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
    return df.set_index("Region")
try:
    df = get_UN_data()
    countries = tab_stats.multiselect(
        "Choose countries", list(df.index), ["France", "Germany", "Poland", "Spain"]
    )
    if not countries:
        tab_stats.error("Please select at least one country.")
    else:
        data = df.loc[countries]
        data /= 1000000.0
        tab_stats.write("### Déchets produits par pays ")
        tab_stats.write(data.sort_index())
 
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
        )
        chart = (
            alt.Chart(data)
            .mark_area(opacity=0.3)
            .encode(
                x="year:T",
                y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
                color="Region:N",
            )
        )
        tab_stats.altair_chart(chart, use_container_width=True)
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
    """
        % e.reason
    )

last_rows = np.random.randn(1, 1)
chart = tab_stats.line_chart(last_rows)
status_text = tab_stats.empty()
progress_bar = tab_stats.progress(0)
for i in range(1, 101):
    new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
    status_text.text("%i%% Complete" % i)
    chart.add_rows(new_rows)
    progress_bar.progress(i)
    last_rows = new_rows
    time.sleep(0.05)
tab_stats.button("Re-run")





### Map ###
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
            get_color="[172, 198, 135, 255]"
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
    font = ImageFont.truetype("arial.ttf", int(max(20, 60 * img_fraction)))
    
    for p in predictions:
        x,y,w,h,proba = p[1]
        color = colorsys.hsv_to_rgb(np.random.random(),1,1)
        random_color=tuple(np.random.choice(range(255),size=3))
        #fill_color = tuple(list(color) + [int(255*0.05)])
        draw.rectangle([(x, y), (w, h)], outline=random_color,  width=8)
        label = f"{p[0]} ({proba:.2f})"
        draw.text((x, y-30), p[0], fill=random_color,font=font)
        
    col2.write("Image avec les déchets détectés :wrench:")
    col2.image(image)
    return predictions

file_upload = tab_predict.file_uploader("Charger une image", type=["png", "jpg", "jpeg"])
col1, col2 = tab_predict.columns(2)
progress_bar = tab_predict.progress(0)

if file_upload is not None:
    
    predictions = detect(upload=file_upload)
    for i in range(1, 101):
        progress_bar.progress(i)
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

