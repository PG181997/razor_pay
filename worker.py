import httpx
from arq.connections import RedisSettings
from arq import Retry


async def web_hook(ctx, webhook_url, amount: int, transaction_id: str):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                webhook_url, json={"amount": amount, "transaction_id": transaction_id}
            )
    except Exception:
        print(f"Failed for transation_id:{transaction_id}")
        raise Retry(defer=5)


web_hook.max_tries = 3


class WorkerSettings:
    redis_settings = RedisSettings(host="localhost", port=6379)
    functions = [web_hook]
