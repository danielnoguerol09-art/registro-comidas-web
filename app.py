from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import pytz   # <-- AGREGADO PARA MANEJAR ZONA HORARIA

app = Flask(__name__)

# Crear tabla si no existe (incluye HORA)
def init_db():
    conn = sqlite3.connect("comidas_web.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS comidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            hora TEXT,
            tipo TEXT,
            descripcion TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


def get_db():
    return sqlite3.connect("comidas_web.db")


@app.route("/", methods=["GET"])
def index():
    conn = get_db()
    c = conn.cursor()

    # Filtros
    filtro_fecha = request.args.get("fecha", "")
    filtro_tipo = request.args.get("tipo", "")

    query = "SELECT fecha, hora, tipo, descripcion FROM comidas"
    params = []

    # Aplicar filtros si existen
    if filtro_fecha or filtro_tipo:
        query += " WHERE"
        if filtro_fecha:
            query += " fecha = ?"
            params.append(filtro_fecha)
        if filtro_tipo:
            if params:
                query += " AND"
            query += " tipo = ?"
            params.append(filtro_tipo)

    query += " ORDER BY id DESC"

    c.execute(query, params)
    registros = c.fetchall()

    # Obtener fechas para el filtro
    c.execute("SELECT DISTINCT fecha FROM comidas ORDER BY fecha DESC")
    fechas_disponibles = [f[0] for f in c.fetchall()]

    conn.close()

    return render_template("index.html",
                           registros=registros,
                           fechas=fechas_disponibles,
                           filtro_fecha=filtro_fecha,
                           filtro_tipo=filtro_tipo)


@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        fecha = request.form["fecha"]
        hora = request.form["hora"]   # Recibe hora del formulario
        tipo = request.form["tipo"]
        descripcion = request.form["descripcion"]

        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO comidas (fecha, hora, tipo, descripcion) VALUES (?, ?, ?, ?)",
                  (fecha, hora, tipo, descripcion))
        conn.commit()
        conn.close()

        return redirect("/")

    # -----------------------------
    # Hora con zona horaria ARG
    # -----------------------------
    tz = pytz.timezone("America/Argentina/Buenos_Aires")
    hora_actual = datetime.now(tz).strftime("%H:%M")

    return render_template("agregar.html", hora_actual=hora_actual)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)