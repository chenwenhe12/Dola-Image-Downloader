# Dola Thread Image Parser API

A small **FastAPI** service that extracts image URLs from a shared thread page on Dola by parsing the HTML/JSON returned by the server.

## ✨ Features

- Accepts a `shareUrl` (or thread ID) plus a login `cookie`.
- Fetches the thread page and extracts image links (`ibyteimg`, `tos-`, `p16-`, etc.) via regex.
- Filters out avatar/icon images, and separates "raw" images from bot-generated ones (`rc_gen_image`).
- Returns a JSON response with the main image list and other variants.

## 🚀 Installation

### Requirements
- Python 3.9+
- pip

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/chenwenhe12/Dola-Image-Downloader.git
cd Dola-Image-Downloader

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install fastapi uvicorn httpx

# 4. Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## 📖 Usage

### Main endpoint

**POST** `/parse-thread-images`

```json
{
  "shareUrl": "https://www.dola.com/thread/abc123xyz",
  "cookie": "session=xxxxx; token=yyyyy"
}
```

**Example response:**

```json
{
  "share_id": "abc123xyz",
  "status_code_from_dola": 200,
  "images_no_watermark": [
    "https://p16-xxx.ibyteimg.com/...raw..."
  ],
  "all_variants": {
    "ibyteimg_other_urls": [
      "https://p16-xxx.ibyteimg.com/...rc_gen_image..."
    ]
  }
}
```

### Health check

- `GET /` — check that the API is running
- `GET /health` — check service status

## ⚠️ Important notes

- The `cookie` is your personal login session on Dola — **never commit or publish this value**. Store it via environment variables or a `.env` file (added to `.gitignore`).
- This tool automates access to and extraction of data from a third-party platform (Dola) by sending your session cookie directly. It does **not** go through any official public API of that platform.

## 📜 Legal & Copyright Notice

Please read carefully before using or distributing this tool:

1. **Terms of Service (ToS):** Most content/image-sharing platforms prohibit scraping, automated access, or bypassing protection mechanisms such as watermarks. Using this tool may violate Dola's ToS and could result in your account being suspended or banned.
2. **Content copyright:** Images obtained through this tool (including ones with watermarks stripped) remain the property of their original creators or the hosting platform. Downloading, storing, editing, or redistributing these images without permission from the copyright holder may violate intellectual property law in your jurisdiction.
3. **Watermark removal:** In many jurisdictions, intentionally removing watermarks or copyright management information from digital content is treated as a separate legal violation (e.g., DMCA §1202 in the United States regarding "Copyright Management Information"), independent of any underlying copyright infringement.
4. **Responsible use:** This source code is provided **for educational and technical research purposes only** (regex parsing, FastAPI, HTML processing). The repository author does not encourage, and is not responsible for, any use that violates a third party's terms of service or applicable law. Users are solely responsible for how they deploy and use this tool.
5. **No official affiliation:** This project is not developed, sponsored, or endorsed by Dola or ByteDance.

If you are a content owner and would like to request removal of this repository, please open an Issue or reach out via the contact information below.

## 📄 License

Released under the [MIT License](LICENSE) — this applies only to the **source code**, not to any content/images extracted through the use of this tool.

## 📬 Contact

- Issues: open one in the **Issues** tab of this repository.
