from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

import requests
from db import Link, get_session
from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse, RedirectResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return RedirectResponse("/docs")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="API Docs",
        swagger_ui_parameters={
            "dom_id": "#swagger-ui",
            "layout": "BaseLayout",
            "deepLinking": True,
            "showExtensions": True,
            "showCommonExtensions": True,
        },
        swagger_css_url="data:text/css;base64,Ym9keSB7IG1heC13aWR0aDogMTAwJSAhaW1wb3J0YW50OyBvdmVyZmxvdzogaGlkZGVuO30=",
    )


@app.api_route(
    "/api/ping",
    methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "HEAD",
        "OPTIONS",
        "TRACE",
    ],
)
def ping():
    db = get_session()
    links = db.query(Link).all()
    result = []
    for link in links:
        response = requests.get(link.url)
        link.status = response.status_code == 200
        link.last_checked = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
        link_dict = link.dict()
        link_dict["last_checked"] = link.last_checked.strftime("%Y-%m-%d %H:%M:%S")
        result.append(link_dict)
        db.commit()
    db.close()
    return JSONResponse({"success": True, "data": result})


@app.get("/api/list")
def list():
    db = get_session()
    links = db.query(Link).all()
    db.close()

    def to_string(link):
        link_dict = link.dict()
        link_dict["last_checked"] = link.last_checked.strftime("%Y-%m-%d %H:%M:%S")
        return link_dict

    links = [to_string(link) for link in links]
    return JSONResponse({"success": True, "data": links})


@app.post("/api/add")
def add(url: Annotated[str, Body(embed=True)], id: Annotated[str, Body(embed=True)]):
    db = get_session()
    link = Link(id=id, url=url)
    db.add(link)
    db.commit()
    db.close()
    return JSONResponse({"success": True, "data": link.dict()})


@app.delete("/api/delete/{id}")
def delete(id: str):
    db = get_session()
    link = db.query(Link).filter(Link.id == id).first()
    db.delete(link)
    db.commit()
    db.close()
    return JSONResponse({"success": True, "data": link.dict()})
