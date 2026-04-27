import httpx

from .config import settings


class BackendClient:
    def __init__(self, access_token: str):
        self._client = httpx.Client(
            base_url=settings.BACKEND_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-API-Version": "1",
            },
        )

    def get(self, path: str, **kwargs):
        return self._client.get(path, **kwargs)

    def post(self, path: str, **kwargs):
        return self._client.post(path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._client.delete(path, **kwargs)
