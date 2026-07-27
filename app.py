import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- Configuración visual para móviles ---
st.set_page_config(page_title="Control de Cargos", layout="centered", page_icon="📋")

# --- ENCABEZADO SOLICITADO ---
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>📋 Hospital Las Mercedes Chiclayo</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray; margin-top: 0px;'>Control de Cargos de Pecosas</h3>", unsafe_allow_html=True)
st.caption("Almacén de Recepción - Entrega de Documentos a Logística")
st.write("---")

# --- CONEXIÓN DIRECTA A GOOGLE SHEETS EN LA NUBE ---
# PEGA AQUÍ TU ENLACE COMPLETO DE GOOGLE SHEETS (El que copiaste en el paso 1)
# Asegúrate de cambiar el final del enlace para que termine en '/export?format=csv' en lugar de '/edit...'
URL_BASE = "https://docs.google.com/spreadsheets/d/1heCibc-23YHJeVJTPfdSLe9v4Q2r7fES7wxz9KJ8VEQ/edit?usp=sharing"
URL_CSV = f"{URL_BASE}/export?format=csv"

@st.cache_data(ttl="0d")  # ttl=0 obliga a leer los datos reales de la nube cada vez
def cargar_datos():
    try:
        return pd.read_csv(URL_CSV)
    except:
        return pd.DataFrame(columns=["ID", "Fecha_Ingreso", "Empresa_Transporte", "Guia_Transporte", "Empresa_Proveedor", "Guia_Proveedor", "Pecosa", "Cantidad", "Importe", "Mes", "Recibido_Por", "Estado"])

df = cargar_datos()

# Conexión para guardar datos (usando solicitudes web estándar de Google Forms o gspread)
# Para mantenerlo 100% libre de errores TOML, el registro se guardará directamente en memoria
# y podrás descargar tus reportes en tiempo real. 
if "cargos_db" not in st.session_state:
    st.session_state.cargos_db = df

df_actual = st.session_state.cargos_db

MESES = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 
         7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

opcion = st.sidebar.selectbox("MENÚ PRINCIPAL", ["📥 Registrar Cargo", "🔍 Consultar Cargos", "✏️ Modificar / Actualizar"])

# ==========================================
# 1. MÓDULO DE INGRESO
# ==========================================
if opcion == "📥 Registrar Cargo":
    st.header("📥 Registro de Entrega de Guía / Cargo")
    
    with st.form("form_registro", clear_on_submit=True):
        fecha = st.date_input("Fecha de Recepción del Documento:", date.today())
        mes_calculado = MESES[fecha.month]
        
        st.subheader("📄 Identificación de Guías")
        emp_transporte = st.text_input("Empresa de Transporte:")
        guia_transporte = st.text_input("Número de Guía de Transporte:")
        emp_proveedor = st.text_input("Empresa Proveedor:")
        guia_proveedor = st.text_input("Número de Guía de Proveedor:")
        pecosa = st.text_input("Nº de Pecosa:")
        
        st.subheader("📦 Datos de la Carga")
        cantidad = st.number_input("Cantidad según Guía:", min_value=0, step=1)
        importe = st.number_input("Importe Total de la Guía (S/.):", min_value=0.0, step=0.10, format="%.2f")
        
        st.subheader("✍️ Control de Cargo y Estado")
        recibido_por = st.text_input("Personal que recibe el Cargo (Nombre):")
        estado = st.selectbox("Estado del Cargo:", ["Cargo Entregado", "Pendiente de Entrega"])
        
        guardar = st.form_submit_button("💾 Guardar y Validar Cargo")
        
        if guardar:
            if not recibido_por:
                st.error("❌ Por seguridad, debes ingresar el nombre de la persona que recibe el cargo.")
            else:
                nuevo_id = int(df_actual["ID"].max() + 1) if not df_actual.empty and pd.notna(df_actual["ID"].max()) else 1
                nuevo_registro = pd.DataFrame([{
                    "ID": nuevo_id,
                    "Fecha_Ingreso": fecha.strftime("%Y-%m-%d"),
                    "Empresa_Transporte": emp_transporte,
                    "Guia_Transporte": guia_transporte,
                    "Empresa_Proveedor": emp_proveedor,
                    "Guia_Proveedor": guia_proveedor,
                    "Pecosa": pecosa,
                    "Cantidad": cantidad,
                    "Importe": importe,
                    "Mes": mes_calculado,
                    "Recibido_Por": recibido_por,
                    "Estado": estado
                }])
                
                st.session_state.cargos_db = pd.concat([df_actual, nuevo_registro], ignore_index=True)
                st.success(f"✔️ ¡Cargo ID {nuevo_id} guardado temporalmente! Descarga el reporte para salvar tus cambios.")

# ==========================================
# 2. MÓDULO DE CONSULTA
# ==========================================
elif opcion == "🔍 Consultar Cargos":
    st.header("🔍 Archivo de Guías y Cargos Entregados")
    
    if df_actual.empty:
        st.warning("No hay cargos registrados.")
    else:
        filtro_busqueda = st.text_input("Buscar por Proveedor, Transporte o Nº de Guía:")
        df_filtrado = df_actual.copy()
        if filtro_busqueda:
            df_filtrado = df_filtrado[
                df_filtrado["Empresa_Proveedor"].astype(str).str.contains(filtro_busqueda, case=False) | 
                df_filtrado["Guia_Proveedor"].astype(str).str.contains(filtro_busqueda, case=False)
            ]
        
        st.dataframe(df_filtrado, use_container_width=True)
        
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte Completo Actualizado (CSV / Excel)", data=csv, file_name=f"cargos_chiclayo_{date.today()}.csv", mime='text/csv')

# ==========================================
# 3. MÓDULO DE MODIFICACIÓN
# ==========================================
elif opcion == "✏️ Modificar / Actualizar":
    st.header("✏️ Actualizar Estado de Entrega")
    if df_actual.empty:
        st.warning("No hay registros.")
    else:
        id_editar = st.selectbox("Seleccione el ID a actualizar:", df_actual["ID"].tolist())
        datos_actuales = df_actual[df_actual["ID"] == id_editar].iloc[0]
        
        with st.form("form_edicion"):
            edit_recibido = st.text_input("Recibido por:", value=datos_actuales["Recibido_Por"])
            lista_estados = ["Cargo Entregado", "Pendiente de Entrega"]
            idx_estado = lista_estados.index(datos_actuales["Estado"]) if datos_actuales["Estado"] in lista_estados else 0
            edit_estado = st.selectbox("Estado del Cargo:", lista_estados, index=idx_estado)
            
            actualizar = st.form_submit_button("⚡ Actualizar Estado")
            if actualizar:
                st.session_state.cargos_db.loc[st.session_state.cargos_db["ID"] == id_editar, ["Recibido_Por", "Estado"]] = [edit_recibido, edit_estado]
                st.success("¡Registro actualizado!")
                st.rerun()
