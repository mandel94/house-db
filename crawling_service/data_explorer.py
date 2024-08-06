from flask import Flask, request, render_template_string, jsonify
from storage import get_db_connection

app = Flask(__name__)


    
@app.route("/")
def index():
    return "This is the main page of the data explorer"


@app.route("/housetable")
def house_tables():
    conn = get_db_connection()
    houses = conn.execute("SELECT * FROM houses").fetchall()
    return jsonify(houses)
    conn.close()
    return render_template_string(
        """
        <h1>Houses Data Explorer</h1>
        <table border="1">
            <tr>
                <th>ID</th>
                <th>Global ID</th>
                <th>Title</th>
                <th>Address</th>
                <th>City</th>
                <th>District</th>
                <th>Description</th>
                <th>Type</th>
                <th>Floor</th>
                <th>Rooms</th>
                <th>Bedrooms</th>
                <th>Kitchen</th>
                <th>Number of Floors</th>
                <th>Furnished</th>
                <th>Balcony</th>
                <th>Terrace</th>
                <th>Heating</th>
                <th>URL</th>
                <th>Living Space (m²)</th>
                <th>Bathrooms</th>
                <th>State</th>
                <th>Construction Year</th>
                <th>Elevator</th>
                <th>Garage/Parking Space</th>
                <th>Energy Class</th>
                <th>Energy Certification</th>
                <th>Air Conditioning</th>
                <th>Price</th>
                <th>Condo Fees</th>
                <th>Agency</th>
                <th>Immobiliare ID</th>
                <th>Last Updated</th>
            </tr>
            {% for house in houses %}
            <tr>
                <td>{{ house['id'] }}</td>
                <td>{{ house['global_id'] }}</td>
                <td>{{ house['title'] }}</td>
                <td>{{ house['address'] }}</td>
                <td>{{ house['city'] }}</td>
                <td>{{ house['district'] }}</td>
                <td>{{ house['description'] }}</td>
                <td>{{ house['type'] }}</td>
                <td>{{ house['floor'] }}</td>
                <td>{{ house['rooms'] }}</td>
                <td>{{ house['bedrooms'] }}</td>
                <td>{{ house['kitchen'] }}</td>
                <td>{{ house['number_of_floors'] }}</td>
                <td>{{ house['furnished'] }}</td>
                <td>{{ house['balcony'] }}</td>
                <td>{{ house['terrace'] }}</td>
                <td>{{ house['heating'] }}</td>
                <td>{{ house['url'] }}</td>
                <td>{{ house['living_space_mq'] }}</td>
                <td>{{ house['bathrooms'] }}</td>
                <td>{{ house['state'] }}</td>
                <td>{{ house['construction_year'] }}</td>
                <td>{{ house['elevator'] }}</td>
                <td>{{ house['garage_parking_space'] }}</td>
                <td>{{ house['energy_class'] }}</td>
                <td>{{ house['energy_certification'] }}</td>
                <td>{{ house['air_conditioning'] }}</td>
                <td>{{ house['price'] }}</td>
                <td>{{ house['condo_fees'] }}</td>
                <td>{{ house['agency'] }}</td>
                <td>{{ house['immobiliare_id'] }}</td>
                <td>{{ house['last_updated'] }}</td>
            </tr>
            {% endfor %}
        </table>
    """,
        houses=houses,
    )


if __name__ == "__main__":
    db = get_db_connection()
    app.run(host="0.0.0.0", port="5001", debug=True)
