from flask import Flask, render_template, request
from models import db, TemperatureRecord, Tag
import requests
import numpy as np



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///temperature.db'
db.init_app(app)

def delete_all_records():
    db.session.query(TemperatureRecord).delete()
    db.session.query(Tag).delete()
    db.session.commit()
def load_data():
    url = "https://data.giss.nasa.gov/gistemp/graphs/graph_data/GISTEMP_Seasonal_Cycle_since_1880/graph.txt"
    response = requests.get(url)
    lines = response.text.split('\n')[5:]  # Skip the header lines

    # Check if data is already loaded
    if TemperatureRecord.query.first() is not None:
        return  # Data already loaded, exit the function

    for line in lines:
        if line.strip():
            year, anomaly = line.split()[:2]
            record = TemperatureRecord(year=float(year), anomaly=float(anomaly))
            db.session.add(record)
            db.session.flush()  # Ensure the record is assigned an ID before associating it with a tag

            # Add tags to the record based on some criteria
            if float(anomaly) > 0:
                tag_name = 'Positive Anomaly'
            elif float(anomaly) < 0:
                tag_name = 'Negative Anomaly'
            else:
                tag_name = 'Zero Anomaly'

            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.flush()  # Ensure the tag is assigned an ID before associating it with a record

            # Check if the tag is already associated with the record
            if not any(t.id == tag.id for t in record.tags):
                record.tags.append(tag)
    db.session.commit()


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of records per page
    paginated_records = TemperatureRecord.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('index.html', records=paginated_records.items, pagination=paginated_records)

@app.route('/analysis')
def analysis():
    average_anomaly = db.session.query(db.func.avg(TemperatureRecord.anomaly)).scalar()
    max_anomaly = db.session.query(db.func.max(TemperatureRecord.anomaly)).scalar()
    min_anomaly = db.session.query(db.func.min(TemperatureRecord.anomaly)).scalar()

    # Calculate the trend (simple linear regression slope)
    records = TemperatureRecord.query.order_by(TemperatureRecord.year).all()
    if len(records) > 1:
        x = [record.year for record in records]
        y = [record.anomaly for record in records]
        slope, intercept = np.polyfit(x, y, 1)
        trend = f"{slope:.2f} °C/year"
    else:
        trend = "Insufficient data"

    top_ten_anomalies = TemperatureRecord.query.order_by(TemperatureRecord.anomaly.desc()).limit(10).all()
    bottom_ten_anomalies = TemperatureRecord.query.order_by(TemperatureRecord.anomaly).limit(10).all()

    return render_template('analysis.html', average_anomaly=average_anomaly,
                        max_anomaly=max_anomaly, min_anomaly=min_anomaly, trend=trend,
                        top_ten_anomalies=top_ten_anomalies, bottom_ten_anomalies=bottom_ten_anomalies)

   

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        delete_all_records()  # This line will delete all records from the database
        load_data()
    app.run(debug=True)
