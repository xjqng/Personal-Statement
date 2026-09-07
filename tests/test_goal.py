"""
目标模块测试：增删改查
"""
from datetime import datetime, timezone, timedelta

# 构造合法目标数据
_now = datetime.now(timezone.utc)
GOAL_DATA = {
    "title": "Test Goal",
    "description": "Test Description",
    "status": "未开始",
    "start_date": _now.isoformat(),
    "end_date": (_now + timedelta(days=365)).isoformat(),
}


async def test_create_goal(client, auth_headers):
    """创建目标"""
    resp = await client.post("/goal/", json=GOAL_DATA, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Test Goal"
    assert data["status"] == "未开始"
    assert "id" in data


async def test_get_goal(client, auth_headers):
    """查询单条目标"""
    create = await client.post("/goal/", json=GOAL_DATA, headers=auth_headers)
    goal_id = create.json()["id"]
    resp = await client.get(f"/goal/{goal_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test Goal"


async def test_list_goals(client, auth_headers):
    """查询目标列表"""
    for i in range(3):
        data = GOAL_DATA.copy()
        data["title"] = f"Goal {i}"
        await client.post("/goal/", json=data, headers=auth_headers)
    resp = await client.get("/goal/", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 3


async def test_update_goal(client, auth_headers):
    """更新目标，验证状态变更"""
    create = await client.post("/goal/", json=GOAL_DATA, headers=auth_headers)
    goal_id = create.json()["id"]
    resp = await client.put(f"/goal/{goal_id}", json={
        "title": "Updated Goal",
        "status": "进行中"
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Goal"
    assert resp.json()["status"] == "进行中"


async def test_delete_goal(client, auth_headers):
    """删除目标后查询返回 404"""
    create = await client.post("/goal/", json=GOAL_DATA, headers=auth_headers)
    goal_id = create.json()["id"]
    resp = await client.delete(f"/goal/{goal_id}", headers=auth_headers)
    assert resp.status_code == 200
    get_resp = await client.get(f"/goal/{goal_id}", headers=auth_headers)
    assert get_resp.status_code == 404
