import pytest
from tpt_service import app


@pytest.fixture
def client():
    app.config['TESTING'] = True

    return app.test_client()
