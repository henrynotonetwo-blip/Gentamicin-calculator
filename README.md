<<<<<<< HEAD
## Gentamicin Dose Calculator (public website)

This repo contains:
- A **calculation module**: `Gentmicin Calculator Code/Calculator Code/calculator.py`
- A **desktop GUI** (tkinter): `Gentmicin Calculator Code/Calculator Code/Gentamicin.py`
- A **web app** (Streamlit): `Gentmicin Calculator Code/Calculator Code/streamlit_app.py`

For easy deployment, the repo root also contains a wrapper:
- `streamlit_app.py` (runs the real Streamlit app)

## Run locally (website)

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

## Deploy publicly (Streamlit Community Cloud)

You do **not** need to buy a domain first.

1) Put this project on GitHub (public or private repo)
2) Go to Streamlit Community Cloud and create a new app
3) Select your GitHub repo + branch
4) Set **Main file path** to:
   - `streamlit_app.py`
5) Deploy → you’ll get a public URL you can share

## Custom domain (optional, later)

You can buy a domain later and point it to your hosted app if your hosting provider supports custom domains.

=======
# Gentamicin-calculator
>>>>>>> f9835a13e23b7431f17377449ea69a29ec1c3c33
