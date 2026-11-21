import pytest
from services.registration_service import register_student,cancel_registration
from services.event_service import create_event
from database.db import get_db_connection

def setup_event(app, seats=1):
    with app.app_context():
        eid=create_event('Test event','2027-02-01',seats)
    return eid

def test_register_duplicate_full_and_cancel(app):
    eid=setup_event(app)
    with app.app_context():
        reg=register_student(eid,'Student One','R1')
        with pytest.raises(ValueError, match='already'):
            register_student(eid,'Student One','R1')
        with pytest.raises(ValueError, match='full'):
            register_student(eid,'Student Two','R2')
        cancel_registration(reg,'R1')
        row=get_db_connection().execute('SELECT registered FROM events WHERE event_id=?',(eid,)).fetchone()
        assert row['registered']==0
        with pytest.raises(ValueError, match='already been cancelled'):
            cancel_registration(reg,'R1')
        assert get_db_connection().execute('SELECT registered FROM events WHERE event_id=?',(eid,)).fetchone()['registered']==0

def test_duplicate_cancelled_registration_still_forbidden(app):
    eid=setup_event(app)
    with app.app_context():
        reg=register_student(eid,'Student','R1'); cancel_registration(reg)
        with pytest.raises(ValueError, match='already'):
            register_student(eid,'Student','R1')
