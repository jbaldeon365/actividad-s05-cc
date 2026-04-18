import streamlit as st
from pymongo import MongoClient
import pandas as pd

# ─── Configuración de página ───
st.set_page_config(
    page_title="Weather Data MongoDB",
    page_icon="🌦️",
    layout="wide"
)

st.title("🌦️ Weather Reports — Sample Weather Data")
st.caption("Consulta reportes meteorológicos desde MongoDB Atlas")

# ─── Conexión MongoDB Atlas ───
try:
    mongo_uri = st.secrets["mongo"]["uri"]
except KeyError:
    st.error(
        "❌ No se encontró mongo.uri en secrets.toml"
    )
    st.stop()

# ─── Sidebar profesional ───
with st.sidebar:
    st.header("🔌 MongoDB Atlas")
    st.markdown(
        """
        **Base de datos:** `sample_weatherdata`  
        **Colección:** `data`  
        **Origen:** Dataset meteorológico MongoDB
        """
    )

# ─── Conexión ───
@st.cache_resource
def get_client(uri):
    return MongoClient(uri)

try:
    client = get_client(mongo_uri)
    db = client["sample_weatherdata"]
    col_weather = db["data"]

    client.admin.command("ping")
    st.sidebar.success("✅ Conectado correctamente")

except Exception as e:
    st.error(f"❌ Error de conexión: {e}")
    st.stop()

# ─── Buscador ───
st.markdown("---")

col1, col2 = st.columns([3, 1])

with col1:
    station = st.text_input(
        "🔍 Buscar estación meteorológica",
        placeholder="Ej: x+47600"
    )

with col2:
    limite = st.selectbox("Resultados máx.", [5, 10, 20, 50], index=1)

if not station:
    st.info("Escribe parte del código de estación meteorológica.")
    st.stop()

# ─── Consulta MongoDB ───
query = {"st": {"$regex": station, "$options": "i"}}
weather = list(col_weather.find(query).limit(limite))

if not weather:
    st.warning("No se encontraron registros.")
    st.stop()

st.success(f"Se encontraron **{len(weather)}** registros meteorológicos")

# ─── Procesar resultados ───
resultados = []

for r in weather:

    coord = r.get("position", {}).get("coordinates", [])

    resultados.append({
        "Estación": r.get("st", "—"),
        "Fecha": r.get("ts", "—"),
        "Temperatura (°C)": r.get("airTemperature", {}).get("value", "—"),
        "Presión": r.get("pressure", {}).get("value", "—"),
        "Viento": r.get("wind", {}).get("speed", {}).get("rate", "—"),
        "Elevación": r.get("elevation", "—"),
        "Longitud": coord[0] if len(coord) >= 2 else None,
        "Latitud": coord[1] if len(coord) >= 2 else None
    })

df = pd.DataFrame(resultados)

# ─── Métricas rápidas ───
st.markdown("### 📊 Resumen rápido")

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("Registros", len(df))

with m2:
    temp_prom = pd.to_numeric(df["Temperatura (°C)"], errors="coerce").mean()
    st.metric("Temp promedio", round(temp_prom, 2) if pd.notnull(temp_prom) else "N/A")

with m3:
    viento_prom = pd.to_numeric(df["Viento"], errors="coerce").mean()
    st.metric("Viento promedio", round(viento_prom, 2) if pd.notnull(viento_prom) else "N/A")

# ─── Tabla ───
st.markdown("### 📋 Resultados")
st.dataframe(df, use_container_width=True, hide_index=True)

# ─── Mapa ───
df_map = df.dropna(subset=["Latitud", "Longitud"]).copy()
df_map = df_map.rename(columns={"Latitud": "latitude", "Longitud": "longitude"})

if not df_map.empty:
    st.markdown("### 🗺️ Ubicación geográfica")
    st.map(df_map[["latitude", "longitude"]])

# ─── Detalle expandible ───
st.markdown("### 📝 Detalle por registro")

for i, r in enumerate(weather):

    with st.expander(f"📌 Estación {r.get('st', '—')}"):

        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"**Fecha:** {r.get('ts', '—')}")
            st.markdown(f"**Elevación:** {r.get('elevation', '—')}")
            st.markdown(f"**Call Letters:** {r.get('callLetters', '—')}")
            st.markdown(f"**Tipo:** {r.get('type', '—')}")

        with c2:
            st.markdown(f"**Temperatura:** {r.get('airTemperature', {}).get('value', '—')}")
            st.markdown(f"**Presión:** {r.get('pressure', {}).get('value', '—')}")
            st.markdown(f"**Viento:** {r.get('wind', {}).get('speed', {}).get('rate', '—')}")
            st.markdown(f"**Visibilidad:** {r.get('visibility', {}).get('distance', {}).get('value', '—')}")
```
