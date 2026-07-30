import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- Configuración visual nativa estándar ---
st.set_page_config(
    page_title="Control de Cargos", 
    layout="centered", 
    page_icon="data:image/jpeg;base64,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"
)
# --- OCULTAR ÚNICAMENTE EL ICONO DE LA HOJA Y EL CERO ---
st.markdown("""
    <style>
        /* Apaga la decoración del indicador de caché manteniendo el botón del menú vivo */
        .stCache, div[class*="stCache"], iframe[title*="cache"], [data-testid="stHeader"] .stCache {
            display: none !important;
            visibility: hidden !important;
            width: 0px !important;
            height: 0px !important;
        }
    </style>
""", unsafe_allow_html=True)
# --- CONTROL DE ACCESO (SISTEMA DE CONTRASEÑA) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

def verificar_password():
    if st.session_state["password_ingresada"] == st.secrets["password_sistema"]:
        st.session_state.autenticado = True
        st.toast("🔓 Acceso concedido.")
    else:
        st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")

# Si NO está autenticado, mostramos la pantalla de bloqueo
if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center;'>🔒 Sistema Protegido</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Introduce la clave de acceso para el Control de Cargos</p>", unsafe_allow_html=True)
    
    st.text_input(
        "Contraseña del Sistema:", 
        type="password", 
        key="password_ingresada", 
        on_change=verificar_password
    )
    st.stop()

# --- Botón de cerrar sesión en la barra lateral ---
if st.sidebar.button("🔒 Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

# --- ENCABEZADO INSTITUCIONAL ---
st.image("https://regionlambayeque.gob.pe", width=90)
st.title("📋 Control de Cargos de Pecosas")
st.subheader("Chiclayo")
st.caption("Almacén de Recepción - Entrega de Documentos a Logística - Hospital Las Mercedes")
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
                st.info("Para guardar registros nuevos en la nube, edita tu Google Sheets. Esta pantalla lee los datos en tiempo real.")

# ==========================================
# 2. MÓDULO DE CONSULTA
# ==========================================
elif opcion == "🔍 Consultar Cargos":
    st.header("🔍 Archivo de Guías y Cargos Entregados")
    
    if df_actual.empty or "html" in str(df_actual.columns).lower():
        st.warning("No hay cargos registrados o la hoja no es pública.")
    else:
        # TÍTULO CLARO EN EL BUSCADOR PARA SABER DÓNDE ESCRIBIR
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
# 3. MÓDULO DE MODIFICACIÓN
# ==========================================
elif opcion == "✏️ Modificar / Actualizar":
    st.header("✏️ Actualizar Estado de Entrega")
    st.info("Para modificar registros, edita directamente las celdas en tu archivo de Google Sheets. El celular actualizará los cambios de inmediato.")
