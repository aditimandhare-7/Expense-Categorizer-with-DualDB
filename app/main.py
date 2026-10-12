import sys
import os
import datetime
from flask import Flask, request, jsonify

# ✅ Add root folder to path so we can import `app` modules directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.mysql_conn import get_mysql_connection
from app.db.mongo_conn import notes_collection
from app.utils.parser import parse_csv
from app.utils.categorizer import predict_category

# ✅ Flask app setup
app = Flask(__name__)

UPLOAD_FOLDER = r"app/uploads"

@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    # ✅ Handle missing file key
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']

    # ✅ Handle no file selected
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # ✅ Save uploaded file to correct path
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    try:
        records = parse_csv(path)
    except Exception as e:
        return jsonify({"error": f"Failed to parse CSV: {str(e)}"}), 400

    conn = get_mysql_connection()
    cursor = conn.cursor()

    for record in records:
        try:
            description = record.get("description", "")
            merchant = record.get("merchant", "")
            amount = float(record.get("amount", 0))
            date = record.get("date", "2025-01-01")
            method = record.get("method", "Unknown")

            category = predict_category(description, merchant)

            cursor.execute("""
                INSERT INTO transactions (user_id, amount, date, payment_method, merchant, category)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                1, amount, date, method, merchant, category
            ))

            txn_id = cursor.lastrowid

            # Handle MongoDB fields
            notes = record.get("notes", "")
            tags_raw = record.get("tags", "[]")
            try:
                tags = eval(tags_raw) if isinstance(tags_raw, str) else tags_raw
            except:
                tags = []

            notes_collection.insert_one({
                "transaction_id": txn_id,
                "notes": notes,
                "tags": tags,
                "timestamp": datetime.datetime.now()
            })

        except Exception as e:
            print(f"Error inserting record: {record}\n{str(e)}")

    conn.commit()
    conn.close()

    return jsonify({"message": "✅ CSV processed and data stored."})


@app.route("/monthly_report/<int:month>/<int:year>", methods=["GET"])
def monthly_report(month, year):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE MONTH(date) = %s AND YEAR(date) = %s
        GROUP BY category
    """, (month, year))

    data = cursor.fetchall()
    conn.close()
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
