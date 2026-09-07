"""
认证模块测试：注册、登录、重复注册、错误密码
"""


async def test_register_success(client):
    """注册成功，返回双 token"""
    resp = await client.post("/auth/register", json={
        "username": "newuser",
        "email": "new@test.com",
        "password": "test12345"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_register_duplicate_username(client, auth_headers):
    """重复用户名注册返回 409"""
    resp = await client.post("/auth/register", json={
        "username": "testuser",
        "email": "another@test.com",
        "password": "test12345"
    })
    assert resp.status_code == 409


async def test_login_success(client, auth_headers):
    """正确用户名密码登录成功"""
    resp = await client.post("/auth/login", data={
        "username": "testuser",
        "password": "test12345"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_wrong_password(client, auth_headers):
    """密码错误返回 401"""
    resp = await client.post("/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert resp.status_code == 401
