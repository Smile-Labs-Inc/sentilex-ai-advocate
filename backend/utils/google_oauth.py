from authlib.integrations.starlette_client import OAuth
import os

oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
    },
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8001/auth/google/callback"),
)
