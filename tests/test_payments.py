async def test_payment(client):
    tenet_res = await client.post(
        "/tenants/", json={"name": "TestCo", "api_key": "key123"}
    )
    assert tenet_res.status_code == 201
    tenant_id = tenet_res.json()["id"]

    #  ================================= From user
    user_res = await client.post(
        "/users/",
        json={
            "username": "TestCo",
            "email": "TestCo@xyz.com",
            "password": "test123",
            "tenent_id": tenant_id,
        },
    )
    assert user_res.status_code == 201

    login_res = await client.post(
        "/login/", json={"email": "TestCo@xyz.com", "password": "test123"}
    )
    assert login_res.status_code == 200
    jwt = login_res.json()

    wallet_res = await client.post(
        "/wallets/", headers={"Authorization": f"Bearer {jwt}"}
    )
    assert wallet_res.status_code == 201
    from_user_wallet_id = wallet_res.json()["response"]["id"]

    wallet_toup_res = await client.patch(
        f"/wallets/{from_user_wallet_id}",
        headers={"Authorization": f"Bearer {jwt}"},
        json={"amount": 1000, "idempotency": "qwerty"},
    )
    assert wallet_toup_res.status_code == 200

    #  ========================================= To user
    to_user_res = await client.post(
        "/users/",
        json={
            "username": "TestCo_to_user",
            "email": "TestCo_to_user@xyz.com",
            "password": "test123",
            "tenent_id": tenant_id,
        },
    )
    assert to_user_res.status_code == 201

    to_userlogin_res = await client.post(
        "/login/", json={"email": "TestCo_to_user@xyz.com", "password": "test123"}
    )
    assert to_userlogin_res.status_code == 200
    jwt_token = to_userlogin_res.json()

    wallet_res_to_user = await client.post(
        "/wallets/", headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert wallet_res_to_user.status_code == 201
    to_user_wallet_id = wallet_res_to_user.json()["response"]["id"]

    transation_res = await client.post(
        "/payments/",
        headers={"Authorization": f"Bearer {jwt}"},
        json={
            "from_wallet_id": from_user_wallet_id,
            "to_wallet_id": to_user_wallet_id,
            "amount": 200,
            "idempotency": "abcd",
        },
    )

    assert transation_res.status_code == 201
