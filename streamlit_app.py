import streamlit as st
import geopandas as gpd
import folium as fol
import folium.features as folf
from streamlit_gsheets import GSheetsConnection
import pyogrio as pyo
import requests
from streamlit_folium import st_folium

## Configurações da Página ##
st.set_page_config(layout="wide")

APP_TITLE = 'Mapeamento da Agricultura Urbana em Contagem'
APP_SUB_TITLE = 'WebApp criado para identificar as Unidades Produtivas Ativas em parceria com a Prefeitura de Contagem'

## Carregar dados do Google Sheets ##
conn = st.connection("gsheets", type=GSheetsConnection)
url = "https://docs.google.com/spreadsheets/d/16t5iUxuwnNq60yG7YoFnJw3RWnko9-YkkAIFGf6xbTM/edit?gid=1832051074#gid=1832051074"
data_ups_sujo = conn.read(spreadsheet=url, worksheet="1832051074")
data_ups = data_ups_sujo.dropna(subset=['Nome','lat', 'lon','Tipo','Regional,'Tiponum'])

## Carregar GeoJSON ##
geojson_url = "https://raw.githubusercontent.com/brmodel/mapeamento_agricultura_contagem/main/regionais_contagem.geojson"
regionais_json = requests.get(geojson_url).json()

# Criar GeoDataFrame
gdf_ups = gpd.GeoDataFrame(
    data_ups,
    geometry=gpd.points_from_xy(data_ups["lon"], data_ups["lat"])
)

## Funções para Estilo ##
def colorir_regional(feature):
    cores = {
        1: "#fbb4ae",
        2: "#b3cde3",
        3: "#ccebc5",
        4: "#decbe4",
        5: "#fed9a6",
        6: "#ffffcc",
        7: "#e5d8bd"
    }
    ##regional_id = feature["properties"]["id"]
    regional_id = feature["properties"].get("id", None)
    cor = cores.get(regional_id, "#fddaec")
    return {
        "fillOpacity": 0.4,
        "fillColor": cor,
        "color": cor,
        "weight": 2,
        "dashArray": "5,5"
    }

## Criar Mapa ##
contagem_base = fol.Map(location=[-44.05183333, -19.93845833], zoom_start=4, tiles="OpenStreetMap", max_zoom=8, src = 4326)

## Remover pontos com coordenadas vazias

# Adicionar GeoJSON
fol.GeoJson(
    regionais_json,
    style_function=colorir_regional,
    tooltip=fol.GeoJsonTooltip(fields=["Nome"], aliases=["Regional:"])
).add_to(contagem_base)

# Adicionar Pontos
for _, row in gdf_ups.iterrows():
    coord = (row["lat"], row["lon"])
    tipo = row["Tiponum"]
    type_color = {
        "1": "green",
        "2": "blue",
        "3": "orange"
    }.get(tipo, "purple")

    fol.Marker(
        location=coord,
        popup=fol.Popup(
            f"Conheça a: {row['Nome']}<br>"
            f"Tipo: {row['Tipo']}<br>"
            f"Regional: {row['Regional']}",
            parse_html=True
        ),
        icon=fol.Icon(color=type_color),
        tooltip=f"Conheça a Unidade Produtiva: {row['Nome']}"
    ).add_to(contagem_base)

## Exibir no Streamlit ##
st.title(APP_TITLE)
st.header(APP_SUB_TITLE)
st_map = st_folium(contagem_base, width=750, height=450)
