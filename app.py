from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import tempfile
from ocr_utils import ocr_image_to_text
from nlp_utils import extract_treatments_from_text
from db_init import init_db, query_hospitals_for_treatment
from math import radians, cos, sin, asin, sqrt

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "medicost.db")

# Initialize DB with sample data if not exists
init_db(DB_PATH)

def haversine(lat1, lon1, lat2, lon2):
    # returns distance in kilometers
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)*2 + cos(lat1) * cos(lat2) * sin(dlon/2)*2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    """
    Accepts a file upload (prescription image/pdf). Responds with OCRed text,
    detected treatments and hospital comparison (sorted by price then distance).
    Request form should include optional 'user_lat' and 'user_lon' to compute distance.
    """
    if 'file' not in request.files:
        return jsonify({"error": "no file part"}), 400

    file = request.files['file']
    if file.filename == "":
        return jsonify({"error": "no selected file"}), 400

    # Save to temp and OCR
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        ocr_text = ocr_image_to_text(tmp_path)
    except Exception as e:
        os.unlink(tmp_path)
        return jsonify({"error": "ocr_failed", "details": str(e)}), 500

    # Extract treatments (list of treatment codes or names)
    detected = extract_treatments_from_text(ocr_text)

    # Get user location if provided (float strings)
    try:
        user_lat = float(request.form.get("user_lat")) if request.form.get("user_lat") else None
        user_lon = float(request.form.get("user_lon")) if request.form.get("user_lon") else None
    except:
        user_lat = user_lon = None

    results = []
    for treat in detected:
        rows = query_hospitals_for_treatment(DB_PATH, treat)
        for r in rows:
            hosp = {
                "hospital_id": r["id"],
                "hospital_name": r["name"],
                "treatment_code": treat,
                "treatment_name": r["treatment_name"],
                "price": r["price"],
                "lat": r["lat"],
                "lon": r["lon"]
            }
            if user_lat is not None and user_lon is not None:
                hosp["distance_km"] = round(haversine(user_lat, user_lon, r["lat"], r["lon"]), 2)
            else:
                hosp["distance_km"] = None
            results.append(hosp)

    # Sort by price ascending, then distance if present
    results.sort(key=lambda x: (x["price"], float(x["distance_km"]) if x["distance_km"] is not None else 999999))

    os.unlink(tmp_path)
    return jsonify({
        "ocr_text": ocr_text,
        "detected_treatments": detected,
        "comparisons": results
    })

if __name__ == "_main_":
    app.run(debug=True, port=5000)