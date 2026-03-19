from frontend.app import app


def test_about_route_renders_successfully():
    client = app.test_client()
    response = client.get('/about')

    assert response.status_code == 200
    assert b'About This Project' in response.data
