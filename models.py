from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('temperature_record_id', db.Integer, db.ForeignKey('temperature_record.id'), primary_key=True)
)

class TemperatureRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Float, nullable=False)
    anomaly = db.Column(db.Float, nullable=False)
    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
                           backref=db.backref('temperature_records', lazy=True))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

