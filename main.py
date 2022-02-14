from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from listings.controllers import listings_router
from auth.controllers import auth_router
from profile.controllers import profile_router

app = FastAPI(default_response_class=ORJSONResponse, title='Real Estate')

app.include_router(listings_router)
app.include_router(auth_router)
app.include_router(profile_router)
