import unittest
import logging
from datetime import datetime

from database import db_engine, DbTable, Request, DbSession


class DatabaseTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(DatabaseTest, self).__init__(*args, **kwargs)
        # logging.basicConfig(level=logging.DEBUG)
        self.init_tests()

    def init_tests(self):
        pass

    def test_memory_database(self):
        # db_debug = True
        db_debug = False
        # Do NOT ever use memory database on the running server, as flask is
        # multi-thread and each thread sees a different instance of the database.
        # Use only for unit tests
        db_path = ':memory:'
        db_driver = 'sqlite'

        # Get engine
        engine = db_engine(db_driver, db_path, debug=db_debug)

        # Create schema
        DbTable.metadata.bind = engine
        DbTable.metadata.create_all()

        # Create a row object
        req = Request(request_id="1234", request_date=datetime.now(),
                      similarity=1.0, status='SUBMITTED',
                      dataset_a='aaaaaaaaaaaa', dataset_b='bbbbbbbbb')

        self.assertIsNone(req.id)
        self.assertEqual(req.request_id, "1234")

        # Create db session
        DbSession.configure(bind=engine)
        session = DbSession()

        # Write the object in DB (no flush yet, so not written. If we query, it will flush before query)
        session.add(req)

        # Issue all the inserts and updates
        session.commit()

        # Query DB
        read_req = session.query(Request).filter_by(request_id='1234').first()
        self.assertIsNotNone(read_req.id)
        self.assertEqual(req, read_req)
        self.assertEqual(read_req.dataset_b, 'bbbbbbbbb')

        session.close()
