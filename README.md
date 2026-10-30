# RegTech365 proposal builder (Python)

The deployment uses two services:

- **Render** runs the FastAPI service in `render-service`. It owns the Google Slides and Drive credentials.
- **Vercel** serves `web/public/index.html` and runs `web/api/proxy.py`. The proxy keeps the Render API key out of the browser.

## Prepare Google Cloud

1. Enable the Google Slides API and Google Drive API in the same Google Cloud project as the service account.
2. Create a service account and download its JSON key.
3. Share the Google Slides template with the service account email as **Editor**.
4. Share the output Drive folder with the service account email as **Editor**.
5. In the template, replace placeholders with the `{{token}}` values in `TOKENS.txt`. Set each optional module tile's alt text/description to values such as `module:aml`.

Keep the JSON key and API keys in platform environment variables. Do not commit them.

## Deploy the Render API

The root `render.yaml` is a Render Blueprint for the API. In Render:

1. Create a **New + > Blueprint** and select this repository, or create a **Web Service** manually.
2. For a manual service, use `render-service` as the root directory, `Python` as the runtime, `pip install -r requirements.txt` as the build command, and `uvicorn main:app --host 0.0.0.0 --port $PORT` as the start command.
3. Add these environment variables:

   - `GOOGLE_SA_JSON`: the complete service-account JSON object on one line
   - `TEMPLATE_ID`: the Google Slides template ID
   - `OUTPUT_FOLDER_ID`: the destination Drive folder ID
   - `API_KEY`: a long random secret
   - `PYTHON_VERSION`: `3.12.3`

4. Deploy and wait for the health check to pass at `https://YOUR-RENDER-SERVICE.onrender.com/health`.

The Render URL should return `{"ok":true}`. `/fields` is protected and should return HTTP 401 without the `x-api-key` header.

## Deploy the Vercel UI

1. Import the same repository into Vercel.
2. Set the project **Root Directory** to `web` and choose the **Other** framework preset. The existing `web/vercel.json` configures the Python function timeout.
3. Add these environment variables for the Production environment:

   - `RENDER_URL`: the Render service URL, without a trailing slash
   - `RENDER_API_KEY`: exactly the same value as Render's `API_KEY`

4. Deploy. Open the Vercel URL and confirm that the form loads module and field data.

## Smoke tests

Check Render directly:

```powershell
curl.exe https://YOUR-RENDER-SERVICE.onrender.com/health
curl.exe -H "x-api-key: YOUR_API_KEY" https://YOUR-RENDER-SERVICE.onrender.com/fields
```

Then check the Vercel proxy:

```powershell
curl.exe "https://YOUR-VERCEL-APP.vercel.app/api/proxy?op=fields"
```

Submit a small proposal from the UI. The first Render request can be slow after a cold start. A successful response provides a Google Slides edit link and a PDF download link.

## Local test

```powershell
cd render-service
pip install -r requirements.txt
$env:GOOGLE_SA_JSON = '{...}'
$env:TEMPLATE_ID = '...'
$env:OUTPUT_FOLDER_ID = '...'
$env:API_KEY = 'local-secret'
uvicorn main:app --host 127.0.0.1 --port 4000
```

In a second terminal:

```powershell
curl.exe -H "x-api-key: local-secret" http://127.0.0.1:4000/fields
```
