import os, re, json, time, datetime as dt
from typing import Any
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import Response
from google.oauth2 import service_account
from googleapiclient.discovery import build
from schema import FIELDS, MODULES, DROPPABLE_SLIDES

creds = service_account.Credentials.from_service_account_info(
    json.loads(os.environ["GOOGLE_SA_JSON"]),
    scopes=["https://www.googleapis.com/auth/presentations", "https://www.googleapis.com/auth/drive"])
slides = build("slides", "v1", credentials=creds, cache_discovery=False)
drive = build("drive", "v3", credentials=creds, cache_discovery=False)
app = FastAPI(
    title="RegTech365 Proposal API",
    description="Internal API for generating proposal decks from the RegTech365 Google Slides template.",
    version="1.0.0",
    contact={"name": "RegTech365 engineering"},
)


class GenerateRequest(BaseModel):
    fields: dict[str, Any] = Field(default_factory=dict)
    modules: list[str] = Field(default_factory=list)
    dropSlides: list[int] = Field(default_factory=list)


class GenerateResponse(BaseModel):
    id: str
    editUrl: str


class FieldsResponse(BaseModel):
    fields: list[dict[str, Any]]
    modules: dict[str, str]
    droppable: dict[int, str]

def guard(key: str):
    if key != os.environ["API_KEY"]:
        raise HTTPException(401, "unauthorised", headers={"WWW-Authenticate": "ApiKey"})


@app.get("/health", tags=["system"])
@app.get("/api/v1/health", tags=["system"])
def health(): return {"ok": True}

@app.get("/fields", response_model=FieldsResponse, include_in_schema=False)
@app.get("/api/v1/fields", response_model=FieldsResponse, tags=["metadata"])
def fields(x_api_key: str = Header("", alias="x-api-key")):
    guard(x_api_key)
    return {"fields": FIELDS, "modules": MODULES, "droppable": DROPPABLE_SLIDES}

@app.post("/generate", response_model=GenerateResponse, include_in_schema=False)
@app.post("/api/v1/proposals", response_model=GenerateResponse, tags=["proposals"])
def generate(body: GenerateRequest, x_api_key: str = Header("", alias="x-api-key")):
    guard(x_api_key)
    F, modules, drop = body.fields, body.modules, body.dropSlides
    today = dt.date.today(); fmt = lambda d: f"{d.day} {d:%B %Y}"
    v = {**F, "issue_date": fmt(today), "valid_until": fmt(today + dt.timedelta(days=30)),
         "doc_ref": f"RT365-{F.get('client_code','')}-{today.year}-{str(int(time.time()))[-3:]}"}
    try:
        pid = drive.files().copy(fileId=os.environ["TEMPLATE_ID"], supportsAllDrives=True,
              body={"name": f"Proposal - {F.get('client_name','')}", "parents": [os.environ["OUTPUT_FOLDER_ID"]]}).execute()["id"]
        pres = slides.presentations().get(presentationId=pid).execute()
        reqs = []
        # 1. remove module tiles/logos not selected (shapes carry Alt text "module:aml" etc.)
        for sl in pres["slides"]:
            for el in sl.get("pageElements", []):
                m = re.match(r"module:(\w+)", el.get("description", ""))
                if m and m.group(1) not in modules:
                    reqs.append({"deleteObject": {"objectId": el["objectId"]}})
        # 2. fill every {{token}}; unanswered ones become empty so no braces ship
        for t in set(re.findall(r"\{\{\w+\}\}", json.dumps(pres))):
            reqs.append({"replaceAllText": {"containsText": {"text": t, "matchCase": True}, "replaceText": str(v.get(t[2:-2], ""))}})
        # 3. drop optional slides
        for n in drop:
            if n in DROPPABLE_SLIDES and n <= len(pres["slides"]):
                reqs.append({"deleteObject": {"objectId": pres["slides"][n - 1]["objectId"]}})
        slides.presentations().batchUpdate(presentationId=pid, body={"requests": reqs}).execute()
        if F.get("share_with"):
            drive.permissions().create(fileId=pid, supportsAllDrives=True,
                body={"type": "user", "role": "writer", "emailAddress": F["share_with"]}).execute()
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"id": pid, "editUrl": f"https://docs.google.com/presentation/d/{pid}/edit"}

@app.get("/pdf/{file_id}", include_in_schema=False)
@app.get("/api/v1/proposals/{file_id}/pdf", tags=["proposals"])
def pdf(file_id: str, x_api_key: str = Header("", alias="x-api-key")):
    guard(x_api_key)
    data = drive.files().export_media(fileId=file_id, mimeType="application/pdf").execute()
    return Response(data, media_type="application/pdf")
