import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- Configuración visual para móviles ---
st.set_page_config(page_title="Control de Cargos", layout="centered", page_icon="📋")

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

# --- ENCABEZADO SOLICITADO ---
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>📋 Control de Cargos de Pecosas</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray; margin-top: 0px;'>Chiclayo</h3>", unsafe_allow_html=True)
st.caption("Almacén de Recepción - Entrega de Documentos a Logística")
st.write("---")

# --- CONEXIÓN DE EXPORTACIÓN DIRECTA ---
ID_HOJA = "1heCibc-23YHJeVJTPfdSLe9v4Q2r7fE777SSSwxz9KJ8VEQ"
URL_CSV = f"https://google.com{ID_HOJA}/export?format=csv"

# Forzar la descarga limpia de datos omitiendo errores del sistema de red anterior
try:
    df_actual = pd.read_csv(URL_CSV)
except Exception as e:
    st.error("⚠️ Error de conexión con los servidores de Google Sheets.")
    df_actual = pd.DataFrame(columns=["ID", "Fecha_Ingreso", "Empresa_Transporte", "Guia_Transporte", "Empresa_Proveedor", "Guia_Proveedor", "Pecosa", "Cantidad", "Importe", "Mes", "Recibido_Por", "Estado"])

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
                st.info("Para guardar registros nuevos en la nube, edita tu Google Sheets. Esta pantalla lee los datos en tiempo real.")

# ==========================================
# 2. MÓDULO DE CONSULTA
# ==========================================
elif opcion == "🔍 Consultar Cargos":
    st.header("🔍 Archivo de Guías y Cargos Entregados")
    
    if df_actual.empty or "html" in str(df_actual.columns).lower():
        st.warning("No hay cargos registrados o la hoja no es pública.")
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
        st.download_button("📥 Descargar Reporte Completo (CSV / Excel)", data=csv, file_name=f"cargos_chiclayo_{date.today()}.csv", mime='text/csv')

# ==========================================
# 3. MÓDULO DE MODIFICACIÓN
# ==========================================
elif opcion == "✏️ Modificar / Actualizar":
    st.header("✏️ Actualizar Estado de Entrega")
    st.info("Para modificar registros, edita directamente las celdas en tu archivo de Google Sheets. El celular actualizará los cambios de inmediato.")
