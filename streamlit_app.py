import streamlit as st
from streamlit_option_menu import option_menu
from enviar import send_email
from google_sheets import googleSheets
from google_calendar import googleCalendar
import uuid
import numpy as np
import datetime as dt
import pytz  # Asegúrate de tener instalada esta librería

page_title = "Club Padel"
page_icon = "img/img2.png"
layout = "centered"

horas = ["09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", "12:00 - 13:00", "13:00 - 14:00", "14:00 - 15:00", "15:00 - 16:00", "16:00 - 17:00", "17:00 - 18:00", "18:00 - 19:00", "19:00 - 20:00"]
canchas = ["Cancha 1", "Cancha 2"]

document = "Gestion-Club-Padel"
sheets = "reservas"
credentials = st.secrets["google"]["credentials_google"]
idcalendar = "developermaximo1@gmail.com"
idcalendar2 = "060c1c526cca8c569ca0b8d71e577cbba38acba4f1dfae49bb0d149f30fdb19c@group.calendar.google.com"
timezone = "America/Montevideo"

##Funciones

def agregar_hora_extra(time):
    parsed_time = dt.datetime.strptime(time, "%H:%M").time()
    new_time = (dt.datetime.combine(dt.date.today(), parsed_time) + dt.timedelta(hours=1, minutes=0)).time()
    return new_time.strftime("%H:%M")

def generate_id():
    return str(uuid.uuid4())

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)

st.image("img/img2.png", width=250)

st.title("Club de Padel")
st.text("Calle direccion, N28")

selected = option_menu(menu_title=None, options=["Reservar", "Canchas", "Detalles"],
                       icons=["calendar-plus", "building", "clipboard-minus"], 
                       orientation="horizontal")

if selected == "Detalles":
    st.subheader("Ubicación:")
    st.markdown("""<iframe src="https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d104723.22942391165!2d-56.1709056!3d-34.891366399999995!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1ses-419!2suy!4v1715566861895!5m2!1ses-419!2suy" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>""", unsafe_allow_html=True)
    
    st.subheader("Horarios")
    dia, hora = st.columns(2)
    
    dia.text("Lunes")
    hora.text("10:00 - 19:00")
    
    dia.text("Martes")
    hora.text("10:00 - 19:00")
    
    dia.text("Miercoles")
    hora.text("10:00 - 19:00")
    
    dia.text("Jueves")
    hora.text("10:00 - 19:00")
    
    dia.text("Viernes")
    hora.text("10:00 - 19:00")

    dia.text("Sabado")
    hora.text("10:00 - 19:00")

    dia.text("Domingo")
    hora.text("10:00 - 19:00")
     
    st.subheader("Contacto")
    st.text("📞 099 299 939")
    
    st.subheader("Instagram")
    st.markdown("Siguenos en [instagram](https://www.instagram.com/)")
    
if selected == "Canchas":
    st.subheader("Cancha 1")
    
    st.write("##")
    st.image("img/pista1.jfif")
    st.image("img/pista2.webp")
    
    st.write("##")
    st.write("##")
    
    st.subheader("Cancha 2")
    
    st.write("##")
    st.image("img/pista3.jpg")
    st.image("img/pista4.jfif")

if selected == "Reservar":
    st.subheader("Reservar")
    
    c1, c2 = st.columns(2)
    
    nombre = c1.text_input("Tu nombre*", placeholder="Nombre Completo")
    email = c2.text_input("Tu email*", placeholder="Email")
    fecha = c1.date_input("Fecha")
    pista = c1.selectbox("Canchas", canchas)
    
    if fecha:
        if pista == "Cancha 1":
            id = idcalendar
        elif pista == "Cancha 2":
            id = idcalendar2
            
        calendar = googleCalendar(credentials, id)
        hours_blocked = calendar.get_events_start_time(str(fecha))
        result_hours = np.setdiff1d(horas, hours_blocked)
    hora = c2.selectbox("Hora", result_hours)
    notas = c2.text_area("", placeholder="Detalles (Alquiler de raquetas, pelotas, etc)")
    
    enviar = st.button("Reservar")
    
    ##BACKEND
    if enviar:
        with st.spinner("Cargando..."):
            if nombre == "":
                st.warning("El nombre es obligatorio")
            elif email == "":
                st.warning("El email es obligatorio")
            else:
                parsed_time = dt.datetime.strptime(hora, "%H:%M").time()
                start_dt = dt.datetime.combine(fecha, parsed_time)
                end_dt = start_dt + dt.timedelta(hours=1)
                
                # Convertir a la zona horaria local
                local_tz = pytz.timezone(timezone)
                start_dt = local_tz.localize(start_dt)
                end_dt = local_tz.localize(end_dt)
                
                # Formatear a ISO 8601
                start_time = start_dt.isoformat()
                end_time = end_dt.isoformat()
                
                calendar = googleCalendar(credentials, id)
                calendar.create_event(nombre, start_time, end_time, timezone)
                
                # GOOGLE SHEETS
                uid = generate_id()
                data = [[nombre, email, pista, str(fecha), hora, notas, uid]]
                gs = googleSheets(credentials, document, sheets)
                range = gs.get_last_row_range()
                gs.write_data(range, data)
                
                send_email(email, nombre, fecha, hora, pista)
                
                st.success("Nos ha llegado tu reserva!")

    