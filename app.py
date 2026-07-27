import streamlit as st
import pandas as pd
from datetime import datetime, date
from gsheetsdb import connect # Alternativamente st.connection para Sheets en versiones recientes

# --- Configuración visual para móviles ---
st.set_page_config(page_title="Control de Cargos", layout="centered", page_icon="📋")

# --- ENCABEZADO SOLICITADO ---
st.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>📋 Control de Cargos de Pecosas</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray; margin-top: 0px;'>Chiclayo</h3>", unsafe_allow_html=True)
st.caption("Almacén de Recepción - Entrega de Documentos a Logística")
st.write("---")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Streamlit maneja las credenciales de la cuenta de servicio de forma nativa a través de secrets
try:
    conn = st.connection("gsheets", type=st.connection.GSheetsConnection)
    # Reemplaza esta URL por el enlace completo de tu hoja de Google Sheets
    URL_HOJA = "https://docs.google.com/spreadsheets/d/1heCibc-23YHJeVJTPfdSLe9v4Q2r7fES7wxz9KJ8VEQ/edit?gid=0#gid=0"
    df = conn.read(spreadsheet=URL_HOJA, ttl="0d")
except Exception as e:
    st.error("Error al conectar con Google Sheets. Verifica las credenciales.")
    df = pd.DataFrame(columns=["ID", "Fecha_Ingreso", "Empresa_Transporte", "Guia_Transporte", "Empresa_Proveedor", "Guia_Proveedor", "Pecosa", "Cantidad", "Importe", "Mes", "Recibido_Por", "Estado"])

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
                nuevo_id = int(df["ID"].max() + 1) if not df.empty and pd.notna(df["ID"].max()) else 1
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
                
                # Actualizar Google Sheets
                df_actualizado = pd.concat([df, nuevo_registro], ignore_index=True)
                conn.update(spreadsheet=URL_HOJA, data=df_actualizado)
                st.success(f"✔️ ¡Cargo ID {nuevo_id} guardado en la nube!")
                st.rerun()

# ==========================================
# 2. MÓDULO DE CONSULTA
# ==========================================
elif opcion == "🔍 Consultar Cargos":
    st.header("🔍 Archivo de Guías y Cargos Entregados")
    
    if df.empty:
        st.warning("No hay cargos registrados.")
    else:
        filtro_busqueda = st.text_input("Buscar por Proveedor, Transporte o Nº de Guía:")
        df_filtrado = df.copy()
        if filtro_busqueda:
            df_filtrado = df_filtrado[
                df_filtrado["Empresa_Proveedor"].astype(str).str.contains(filtro_busqueda, case=False) | 
                df_filtrado["Guia_Proveedor"].astype(str).str.contains(filtro_busqueda, case=False)
            ]
        
        st.dataframe(df_filtrado, use_container_width=True)
        
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte en Excel (CSV)", data=csv, file_name="reporte.csv", mime='text/csv')

# ==========================================
# 3. MÓDULO DE MODIFICACIÓN
# ==========================================
elif opcion == "✏️ Modificar / Actualizar":
    st.header("✏️ Actualizar Estado de Entrega")
    if df.empty:
        st.warning("No hay registros.")
    else:
        id_editar = st.selectbox("Seleccione el ID a actualizar:", df["ID"].tolist())
        datos_actuales = df[df["ID"] == id_editar].iloc[0]
        
        with st.form("form_edicion"):
            edit_recibido = st.text_input("Recibido por:", value=datos_actuales["Recibido_Por"])
            lista_estados = ["Cargo Entregado", "Pendiente de Entrega"]
            idx_estado = lista_estados.index(datos_actuales["Estado"]) if datos_actuales["Estado"] in lista_estados else 0
            edit_estado = st.selectbox("Estado del Cargo:", lista_estados, index=idx_estado)
            
            actualizar = st.form_submit_button("⚡ Actualizar Estado")
            if actualizar:
                df.loc[df["ID"] == id_editar, ["Recibido_Por", "Estado"]] = [edit_recibido, edit_estado]
                conn.update(spreadsheet=URL_HOJA, data=df)
                st.success("¡Registro actualizado en la nube!")
                st.rerun()