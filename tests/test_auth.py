def test_manager_login_and_summary_with_zero_registrations(client, manager_id, app):
    assert client.get('/manager/').status_code == 302
    response=client.post('/manager/login',data={'username':'manager','password':'wrong'})
    assert b'Invalid username or password' in response.data
    client.post('/manager/login',data={'username':'manager','password':'a-strong-test-password'})
    with app.app_context():
        from database.db import get_db_connection
        get_db_connection().execute("INSERT INTO events(name,event_date,seats) VALUES('Empty event','2027-02-01',5)")
    response=client.get('/manager/summary')
    assert response.status_code==200
    assert b'Empty event' in response.data and b'0%' in response.data
