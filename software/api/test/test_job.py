DATA_VALID = {
    "source": "test",
    "ext_id": "001",
    "title": "Backend Intern",
    "company": "PT Anu",
    "url": "http://a.com",
}


async def test_ingest_created(client, bersih):
    response = await client.post("/jobs", json=DATA_VALID)
    assert response.status_code == 201


async def test_ingest_duplicate(client, bersih):
    response = await client.post("/jobs", json=DATA_VALID)
    response1 = await client.post("/jobs", json=DATA_VALID)
    assert response.status_code == 201
    assert response1.status_code == 200


async def test_ingest_missing(client, bersih):
    data = DATA_VALID.copy()
    del data["title"]
    response = await client.post("/jobs", json=data)
    assert response.status_code == 422


async def test_get_job_not_found(client):
    response = await client.get("/jobs/999")
    assert response.status_code == 404


async def test_get_job_bad_id(client):
    response = await client.get("/jobs/abc")
    assert response.status_code == 422
