
from flask import Flask, render_template, request, session, redirect, url_for
import requests
import sqlite3
from database.db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "agrismart_development_key"  # Replace

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/crop", methods=["GET", "POST"])
def crop():

    if "farmer_id" not in session:
        return redirect(url_for("login"))

    recommendation = None

    if request.method == "POST":

        nitrogen = float(request.form["nitrogen"])
        phosphorus = float(request.form["phosphorus"])
        potassium = float(request.form["potassium"])
        temperature = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        ph = float(request.form["ph"])
        rainfall = float(request.form["rainfall"])

        # Expanded Rule-Based Crop Recommendation

        if rainfall >= 150 and 5.5 <= ph <= 7.5:
            recommendation = "Rice"

        elif rainfall >= 80 and temperature >= 20:
            recommendation = "Maize"

        elif rainfall >= 50 and 20 <= temperature <= 30 and 6 <= ph <= 7.5:
            recommendation = "Soybean"

        elif rainfall >= 50 and temperature >= 20 and phosphorus >= 25:
            recommendation = "Chickpea"

        elif rainfall < 80 and temperature >= 25 and 5.5 <= ph <= 7.5:
            recommendation = "Groundnut"

        elif rainfall >= 50 and temperature >= 25 and potassium >= 30:
            recommendation = "Cotton"

        elif rainfall >= 40 and temperature >= 20 and 5.5 <= ph <= 7:
            recommendation = "Sunflower"

        elif rainfall < 100 and temperature >= 20 and phosphorus >= 20:
            recommendation = "Mustard"

        elif rainfall >= 40 and temperature >= 25 and nitrogen >= 20:
            recommendation = "Black Gram"

        elif rainfall >= 40 and temperature >= 25 and humidity >= 40:
            recommendation = "Green Gram"

        elif rainfall < 100 and temperature >= 25:
            recommendation = "Sorghum"

        else:
            recommendation = "Sesame"

        # Save Recommendation in SQLite

        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO crop_history
                (farmer_id, nitrogen, phosphorus, potassium,
                 temperature, humidity, ph, rainfall, recommended_crop)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["farmer_id"],
                    nitrogen,
                    phosphorus,
                    potassium,
                    temperature,
                    humidity,
                    ph,
                    rainfall,
                    recommendation
                )
            )

            connection.commit()

        finally:
            connection.close()

    return render_template(
        "crop.html",
        recommendation=recommendation
    )   

@app.route("/weather", methods=["GET", "POST"])
def weather():

    if "farmer_id" not in session:
        return redirect(url_for("login"))

    weather_data = None
    error = None

    if request.method == "POST":

        city = request.form["city"].strip()

        try:
            # Find city coordinates
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"

            geo_response = requests.get(
                geo_url,
                params={"name": city, "count": 1},
                timeout=15
            )

            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if not geo_data.get("results"):
                error = "City not found. Please try again."

            else:
                place = geo_data["results"][0]

                latitude = place["latitude"]
                longitude = place["longitude"]
                city_name = place["name"]

                # Get current weather
                weather_url = "https://api.open-meteo.com/v1/forecast"

                response = requests.get(
                    weather_url,
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"
                    },
                    timeout=15
                )

                response.raise_for_status()
                data = response.json()
                current = data["current"]

                weather_data = {
                    "city": city_name,
                    "temperature": current["temperature_2m"],
                    "humidity": current["relative_humidity_2m"],
                    "wind": current["wind_speed_10m"]
                }

                # Save Weather History in SQLite

                connection = get_db_connection()

                try:
                    connection.execute(
                        """
                        INSERT INTO weather_history
                        (farmer_id, city, temperature, humidity, wind)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            session["farmer_id"],
                            city_name,
                            current["temperature_2m"],
                            current["relative_humidity_2m"],
                            current["wind_speed_10m"]
                        )
                    )

                    connection.commit()

                finally:
                    connection.close()

        except (requests.RequestException, KeyError, ValueError):
            error = "Unable to fetch weather. Please try again."

    return render_template(
        "weather.html",
        weather=weather_data,
        error=error
    )

@app.route("/disease", methods=["GET", "POST"])
def disease():

    if "farmer_id" not in session:
        return redirect(url_for("login"))

    result = None
    advice = None
    medicine = None
    usage = None
    prevention = None

    if request.method == "POST":

        plant = request.form["plant"]
        symptom = request.form["symptom"]

        # Rule-Based Disease Identification

        if plant == "Tomato" and symptom == "brown":
            result = "Possible Early Blight"
            advice = "Remove affected leaves and avoid overhead watering."
            medicine = "Mancozeb-based registered fungicide"
            usage = "Use only a product registered for tomato early blight. Follow the exact label dose, dilution and waiting period."
            prevention = "Avoid wetting leaves, maintain proper spacing and remove infected plant debris."

        elif plant == "Tomato" and symptom == "curling":
            result = "Possible Leaf Curl"
            advice = "Check for whiteflies and inspect plant health."
            medicine = "No single medicine cures viral leaf curl."
            usage = "Control whiteflies using locally approved methods and products according to their labels."
            prevention = "Remove severely affected plants, control weeds and use healthy seedlings."

        elif plant == "Rice" and symptom == "brown":
            result = "Possible Brown Spot"
            advice = "Monitor the crop and seek local agricultural advice."
            medicine = "Registered rice brown spot fungicide"
            usage = "Confirm the disease and follow the registered product label for rice."
            prevention = "Use healthy seeds, maintain balanced nutrients and avoid water stress."

        elif plant == "Potato" and symptom == "white":
            result = "Possible Powdery Mildew"
            advice = "Improve airflow and seek expert confirmation."
            medicine = "Sulphur-based registered fungicide"
            usage = "Use only if registered for the confirmed disease and potato. Follow label directions."
            prevention = "Maintain plant spacing, remove infected debris and monitor leaves regularly."

        elif symptom == "yellow":
            result = "Possible Nutrient Deficiency"
            advice = "Check soil nutrients and inspect watering conditions."
            medicine = "No specific medicine can be recommended without identifying the deficient nutrient."
            usage = "Test the soil or plant tissue before selecting a fertilizer."
            prevention = "Maintain balanced fertilization and proper irrigation."

        else:
            result = "Cause Not Identified"
            advice = "Please consult an agricultural expert."
            medicine = "No medicine recommended until the cause is identified."
            usage = "Get the plant examined before applying pesticides or fungicides."
            prevention = "Maintain field hygiene and monitor the crop regularly."

        # Save Disease Screening History

        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO disease_history
                (farmer_id, plant, symptom, result, advice)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session["farmer_id"],
                    plant,
                    symptom,
                    result,
                    advice
                )
            )

            connection.commit()

        finally:
            connection.close()

    return render_template(
        "disease.html",
        result=result,
        advice=advice,
        medicine=medicine,
        usage=usage,
        prevention=prevention
    )
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        connection = get_db_connection()

        try:
            farmer = connection.execute(
                "SELECT * FROM farmers WHERE email = ?",
                (email,)
            ).fetchone()
        finally:
            connection.close()

        if farmer and check_password_hash(
            farmer["password"], password
        ):
            session["farmer_id"] = farmer["farmer_id"]
            session["farmer_name"] = farmer["farmer_name"]

            return redirect(url_for("dashboard"))

        else:
            error = "Invalid email or password!"

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    success = None

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            error = "Passwords do not match!"

        elif len(password) < 8:
            error = "Password must contain at least 8 characters!"

        else:
            connection = get_db_connection()

            try:
                hashed_password = generate_password_hash(password)

                connection.execute(
                    """INSERT INTO farmers
                    (farmer_name, email, password)
                    VALUES (?, ?, ?)""",
                    (name, email, hashed_password)
                )

                connection.commit()
                success = "Registration successful! Please login."

            except sqlite3.IntegrityError:
                error = "Email already registered!"

            finally:
                connection.close()

    return render_template(
        "register.html",
        error=error,
        success=success
    )

@app.route("/dashboard")
def dashboard():

    if "farmer_id" not in session:
        return redirect(url_for("login"))

    farmer_id = session["farmer_id"]

    connection = get_db_connection()

    try:
        crop_count = connection.execute(
            "SELECT COUNT(*) FROM crop_history WHERE farmer_id = ?",
            (farmer_id,)
        ).fetchone()[0]

        disease_count = connection.execute(
            "SELECT COUNT(*) FROM disease_history WHERE farmer_id = ?",
            (farmer_id,)
        ).fetchone()[0]

        weather_count = connection.execute(
            "SELECT COUNT(*) FROM weather_history WHERE farmer_id = ?",
            (farmer_id,)
        ).fetchone()[0]

    finally:
        connection.close()

    return render_template(
        "dashboard.html",
        crop_count=crop_count,
        disease_count=disease_count,
        weather_count=weather_count
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/reports")
def reports():

    if "farmer_id" not in session:
        return redirect(url_for("login"))

    farmer_id = session["farmer_id"]

    connection = get_db_connection()

    try:
        # Summary Statistics
        crop_count = connection.execute(
            "SELECT COUNT(*) FROM crop_history WHERE farmer_id = ?",
            (farmer_id,)
        ).fetchone()[0]

        disease_count = connection.execute(
            "SELECT COUNT(*) FROM disease_history WHERE farmer_id = ?",
            (farmer_id,)
        ).fetchone()[0]

        weather_count = connection.execute(
            "SELECT COUNT(*) FROM weather_history WHERE farmer_id = ?",
            (farmer_id,)
        ).fetchone()[0]

        # Crop-wise Analysis
        crop_data = connection.execute(
            """
            SELECT recommended_crop, COUNT(*) AS total
            FROM crop_history
            WHERE farmer_id = ?
            GROUP BY recommended_crop
            """,
            (farmer_id,)
        ).fetchall()

        # Disease-wise Analysis
        disease_data = connection.execute(
            """
            SELECT result, COUNT(*) AS total
            FROM disease_history
            WHERE farmer_id = ?
            GROUP BY result
            """,
            (farmer_id,)
        ).fetchall()

        # Recent Weather Records
        weather_data = connection.execute(
            """
            SELECT city, temperature, humidity, wind, created_at
            FROM weather_history
            WHERE farmer_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 10
            """,
            (farmer_id,)
        ).fetchall()

        # Recent Activities
        recent_crops = connection.execute(
            """
            SELECT recommended_crop AS activity, created_at,
                   'Crop Recommendation' AS activity_type
            FROM crop_history
            WHERE farmer_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 5
            """,
            (farmer_id,)
        ).fetchall()

        recent_diseases = connection.execute(
            """
            SELECT result AS activity, created_at,
                   'Disease Screening' AS activity_type
            FROM disease_history
            WHERE farmer_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 5
            """,
            (farmer_id,)
        ).fetchall()

        recent_activities = sorted(
            list(recent_crops) + list(recent_diseases),
            key=lambda x: x["created_at"],
            reverse=True
        )[:8]

    finally:
        connection.close()

    return render_template(
        "reports.html",
        crop_count=crop_count,
        disease_count=disease_count,
        weather_count=weather_count,
        crop_data=[dict(row) for row in crop_data],
        disease_data=[dict(row) for row in disease_data],
        weather_data=[dict(row) for row in reversed(weather_data)],
        recent_activities=recent_activities
    )


@app.route("/growth")
def growth():
    if "farmer_id" not in session:
        return redirect(url_for("login"))

    return render_template("growth.html")


if __name__ == "__main__":
    app.run(debug=True)
