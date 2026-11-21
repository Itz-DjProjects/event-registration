def login(client):
    return client.post('/manager/login', data={'username':'manager','password':'a-strong-test-password'})

def test_event_create_and_protected(client, manager_id):
    assert client.get('/manager/').status_code == 302
    login(client)
    response = client.post('/manager/events/add', data={'name':'Lab Fest','event_date':'2027-02-01','seats':'10'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Lab Fest' in response.data

def test_capacity_reduction_and_delete_restrictions(client, manager_id, app):
    from database.db import get_db_connection
    with app.app_context():
        conn=get_db_connection(); cur=conn.execute("INSERT INTO events(name,event_date,seats,registered) VALUES('Event','2027-02-01',2,1)"); eid=cur.lastrowid
        conn.execute("INSERT INTO registrations(event_id,student_name,roll_no) VALUES(?,?,?)",(eid,'Student','R1'))
    login(client)
    response=client.post(f'/manager/events/{eid}/edit',data={'name':'Event','event_date':'2027-02-01','seats':'0'},follow_redirects=True)
    assert b'positive' in response.data
    response=client.post(f'/manager/events/{eid}/delete',follow_redirects=True)
    assert b'cannot be deleted' in response.data
