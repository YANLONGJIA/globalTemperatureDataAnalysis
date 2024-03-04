import unittest
from app import app, db, TemperatureRecord

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        # Set up an application context and test client
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            # Initialize the database
            db.create_all()

    def tearDown(self):
        # Remove the database after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_index_page(self):
        # Test the index page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Temperature Records', response.data)

    def test_analysis_page(self):
        # Test the analysis page
        response = self.client.get('/analysis')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Global Temperature Data Analysis', response.data)

    def test_data_loading(self):
        # Test data loading into the database
        with self.app.app_context():
            record = TemperatureRecord(year=2020, anomaly=1.2)
            db.session.add(record)
            db.session.commit()
            result = TemperatureRecord.query.filter_by(year=2020).first()
            self.assertIsNotNone(result)
            self.assertEqual(result.anomaly, 1.2)

    def test_pagination(self):
        # Test pagination on the index page
        with self.app.app_context():
            for i in range(15):
                record = TemperatureRecord(year=2000 + i, anomaly=0.5 + i)
                db.session.add(record)
            db.session.commit()

        response = self.client.get('/')
        self.assertIn(b'Next', response.data)  # Check if the 'Next' button is present

        response = self.client.get('/?page=2')
        self.assertIn(b'Previous', response.data)  # Check if the 'Previous' button is present

if __name__ == '__main__':
    unittest.main()
