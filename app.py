import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- Configuración visual nativa estándar ---
st.set_page_config(
    page_title="Control de Cargos", 
    layout="centered", 
    page_icon="🚑"
)

# --- 🎨 TUNEO DEFINITIVO Y LIMPIO: MÁXIMA LEGIBILIDAD EN MÓVILES ---
st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] {
            background-color: #e3f2fd !important;
        }
        header, [data-testid="stHeader"], div[data-testid="stDecoration"], .stCache {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
            opacity: 0 !important;
        }
        [data-testid="stElementToolbar"], div[data-testid="stElementToolbar"] {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
            width: 0px !important;
            opacity: 0 !important;
        }
        div[data-testid="stDateInput"] button, div[data-testid="stDateInput"] input, div[data-baseweb="calendar"] * {
            background-color: #ffffff !important;
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }
        html, body, .stMarkdown, p, label, span, caption, .stCaption {
            color: #0d233a !important;
            -webkit-text-fill-color: #0d233a !important;
            font-weight: 500 !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #0b3c5d !important;
            -webkit-text-fill-color: #0b3c5d !important;
            font-weight: bold !important;
        }
        button[data-baseweb="tab"] p {
            color: #0d233a !important;
            -webkit-text-fill-color: #0d233a !important;
            font-size: 16px !important;
            font-weight: bold !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] p {
            color: #0077b6 !important;
            -webkit-text-fill-color: #0077b6 !important;
        }
        .stTextInput input, .stNumberInput input, .stSelectbox div {
            color: #000000 !important;
            background-color: #ffffff !important;
            -webkit-text-fill-color: #000000 !important;
            border: 2px solid #328cc1 !important;
            border-radius: 8px !important;
        }
        div.stButton > button, div.stFormSubmitButton > button, .stDownloadButton > button {
            background-color: #328cc1 !important;
            color: white !important;
            -webkit-text-fill-color: white !important;
            border-radius: 12px !important;
            border: none !important;
            font-weight: bold !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- CONTROL DE ACCESO DOS NIVELES (ADMINISTRADOR / CONSULTA) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol" not in st.session_state:
    st.session_state.rol = None  # Puede ser 'admin' o 'consulta'

def verificar_password():
    password_ingresada = st.session_state["password_ingresada"]
    
    if password_ingresada == st.secrets["password_sistema"]:
        st.session_state.autenticado = True
        st.session_state.rol = "admin"
        st.toast("🔓 Acceso Administrador concedido.")
    elif password_ingresada == st.secrets["password_consulta"]:
        st.session_state.autenticado = True
        st.session_state.rol = "consulta"
        st.toast("🔍 Acceso de Consulta concedido.")
    else:
        st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")

# Si NO está autenticado, mostramos la pantalla de bloqueo
if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center;'>🔒 Sistema Protegido</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Introduce tu clave de acceso autorizada</p>", unsafe_allow_html=True)
    
    st.text_input(
        "Contraseña del Sistema:", 
        type="password", 
        key="password_ingresada", 
        on_change=verificar_password
    )
    st.stop()

# --- ENCABEZADO INSTITUCIONAL ---
col1, col2 = st.columns(2)
with col1:
    st.markdown("<h1 style='font-size: 55px; margin: 0px;'>🚑</h1>", unsafe_allow_html=True)
with col2:
    st.markdown("<h2 style='margin-top: 0px; margin-bottom: 0px;'>Hospital Regional Docente Las Mercedes Chiclayo</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top: 0px; margin-bottom: 0px;'>Control de Cargos de Pecosas</h4>", unsafe_allow_html=True)

st.caption("Gustavo Taboada B.")
st.write("---")

# --- CONEXIÓN DE EXPORTACIÓN DIRECTA ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSzt4dQwOVkz-ncXFWwGyWY6tt6xqAhgubPsBNSM7EE8asRvtTQ8KFYBPnFkd9kFg_dhmlyciWeHcwI/pub?output=csv"

try:
    df_actual = pd.read_csv(URL_CSV)
except Exception as e:
    st.error("⚠️ Error de conexión con los servidores de Google Sheets.")
    df_actual = pd.DataFrame(columns=["ID", "Fecha_Ingreso", "Empresa_Transporte", "Guia_Transporte", "Empresa_Proveedor", "Guia_Proveedor", "Pecosa", "Cantidad", "Importe", "Mes", "Recibido_Por", "Estado"])

MESES = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 
         7: "Julio", 8: "Agosto", 9: "Setiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}


# --- 🚀 FILTRADO INTELIGENTE DE MENÚ SEGÚN EL ROL ---
if st.session_state.rol == "admin":
    # El administrador ve las 3 pestañas normales
    tab_registrar, tab_consultar, tab_modificar = st.tabs(["📥 Registrar", "🔍 Consultar", "✏️ Modificar"])
else:
    # El personal de consulta SOLO ve la pestaña de consultar
    tab_consultar = st.tabs(["🔍 Consultar"])[0]
    tab_registrar = None
    tab_modificar = None


# ==========================================
# 1. MÓDULO DE INGRESO (SOLO ADMIN)
# ==========================================
if tab_registrar:
    with tab_registrar:
        st.header("📥 Registro de Entrega de Guía / Cargo")
        with st.form("form_registro", clear_on_submit=True):
            fecha = st.date_input("Fecha de Recepción del Documento:", date.today(), format="DD/MM/YYYY")
            emp_transporte = st.text_input("Empresa de Transporte:")
            guia_transporte = st.text_input("Número de Guía de Transporte:")
            emp_proveedor = st.text_input("Empresa Proveedor:")
            guia_proveedor = st.text_input("Número de Guía de Proveedor:")
            pecosa = st.text_input("Nº de Pecosa:")
            cantidad = st.number_input("Cantidad según Guía:", min_value=0, step=1)
            importe = st.number_input("Importe Total de la Guía (S/.):", min_value=0.0, step=0.10, format="%.2f")
            recibido_por = st.text_input("Personal que recibe el Cargo (Nombre):")
            estado = st.selectbox("Estado del Cargo:", ["Cargo Entregado", "Pendiente de Entrega"])
            
            guardar = st.form_submit_button("💾 Guardar y Validar Cargo")
            if guardar:
                if not recibido_por:
                    st.error("❌ Por seguridad, debes ingresar el nombre de la persona que recibe el cargo.")
                else:
                    st.info("Para guardar registros nuevos en la nube, edita tu Google Sheets. Esta pantalla lee los datos en tiempo real.")

# ==========================================
# 2. MÓDULO DE CONSULTA (DISPONIBLE PARA TODOS)
# ==========================================
with tab_consultar:
    st.header("🔍 Archivo de Guías y Cargos Entregados")
    if df_actual.empty or "html" in str(df_actual.columns).lower():
        st.warning("No hay cargos registrados o la hoja no es pública.")
    else:
        filtro_busqueda = st.text_input("Escribe aquí el Proveedor o Guía para buscar:")
        df_filtrado = df_actual.copy()
        if filtro_busqueda:
            df_filtrado = df_filtrado[
                df_filtrado["Empresa_Proveedor"].astype(str).str.contains(filtro_busqueda, case=False) | 
                df_filtrado["Guia_Proveedor"].astype(str).str.contains(filtro_busqueda, case=False)
            ]
        
        st.dataframe(df_filtrado, use_container_width=True)
        
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte Completo (CSV / Excel)", data=csv, file_name=f"cargos_chiclayo_{date.today()}.csv", mime='text/csv')

# ==========================================
# 3. MÓDULO DE MODIFICACIÓN (SOLO ADMIN)
# ==========================================
if tab_modificar:
    with tab_modificar:
        st.header("✏️ Actualizar Estado de Entrega")
        st.info("Para modificar registros, edita directamente las celdas en tu archivo de Google Sheets. El celular actualizará los cambios de inmediato.")

# --- 🔒 BOTÓN DE CERRAR SESIÓN ---
st.write("---")
if st.button("🔒 Cerrar Sesión del Sistema"):
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.rerun()
