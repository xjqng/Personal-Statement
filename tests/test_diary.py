"""
日记模块测试：增删改查 + 未授权访问
"""


async def test_create_diary(client, auth_headers):
    """创建日记"""
    resp = await client.post("/diary/", json={
        "title": "Test Diary",
        "content": "Test Content"
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Test Diary"
    assert data["content"] == "Test Content"
    assert "id" in data


async def test_get_diary(client, auth_headers):
    """查询单条日记"""
    create = await client.post("/diary/", json={
        "title": "Test",
        "content": "Content"
    }, headers=auth_headers)
    diary_id = create.json()["id"]
    resp = await client.get(f"/diary/{diary_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test"


async def test_list_diaries(client, auth_headers):
    """查询日记列表"""
    for i in range(3):
        await client.post("/diary/", json={
            "title": f"Diary {i}",
            "content": f"Content {i}"
        }, headers=auth_headers)
    resp = await client.get("/diary/", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 3


async def test_update_diary(client, auth_headers):
    """更新日记，验证部分更新"""
    create = await client.post("/diary/", json={
        "title": "Old",
        "content": "Old"
    }, headers=auth_headers)
    diary_id = create.json()["id"]
    resp = await client.put(f"/diary/{diary_id}", json={
        "title": "New"
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "New"
    assert resp.json()["content"] == "Old"


async def test_delete_diary(client, auth_headers):
    """删除日记后查询返回 404"""
    create = await client.post("/diary/", json={
        "title": "To Delete",
        "content": "Content"
    }, headers=auth_headers)
    diary_id = create.json()["id"]
    resp = await client.delete(f"/diary/{diary_id}", headers=auth_headers)
    assert resp.status_code == 200
    get_resp = await client.get(f"/diary/{diary_id}", headers=auth_headers)
    assert get_resp.status_code == 404


async def test_unauthorized_access(client):
    """未携带 token 访问返回 401"""
    resp = await client.get("/diary/")
    assert resp.status_code == 401
