import re
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI()

class ThreadRequest(BaseModel):
    shareUrl: str
    cookie: Optional[str] = None

def extract_share_id(url: str) -> Optional[str]:
    """Extract thread ID from Dola share URL"""
    m = re.search(r"/thread/([a-zA-Z0-9]+)", url)
    return m.group(1) if m else (url if url.isalnum() else None)

def harvest_ibyteimg_urls(raw_text: str):
    """
    Extract ByteDance image URLs from HTML/JSON text
    
    Step 1: Completely remove all types of escape slash encoding from ByteDance
    Step 2: Main regex - Allows colon ':' and question mark '?' in the body so signatures aren't truncated
    Step 3: Fallback regex for URLs without query parameters
    Step 4: Clean and filter URLs
    """
    # Step 1: Remove all escape slash encodings from ByteDance
    cleaned_text = raw_text
    cleaned_text = cleaned_text.replace(r"\\u002f", "/").replace(r"\\u002F", "/")
    cleaned_text = cleaned_text.replace(r"\u002f", "/").replace(r"\u002F", "/")
    cleaned_text = cleaned_text.replace(r"\/", "/")
    cleaned_text = cleaned_text.replace("&amp;", "&")

    # Step 2: Main regex - Allows ':' and '?' in body to avoid cutting off signatures
    pattern = r'https://[a-zA-Z0-9\-\.]+(?:ibyteimg|tos-|volcengine|byteimg|p16-|p19-|p26-)[^\s"\':<>\[\]\{\}\\\\]*[:\?][^\s"\'<>\[\]\{\}\\\\]*'
    matches = re.findall(pattern, cleaned_text)
    
    # Step 3: Fallback regex for URLs without trailing parameters
    fallback_pattern = r'https://[a-zA-Z0-9\-\.]+(?:ibyteimg|tos-|volcengine|byteimg|p16-|p19-|p26-)[^\s"\':<>\[\]\{\}\\\\]*'
    matches.extend(re.findall(fallback_pattern, cleaned_text))
    
    raw_images = set()
    other_images = set()
    
    for url in matches:
        # Clean up garbage characters from JSON syntax at the end of URLs
        # Remove HTML entities if present
        url_clean = url.split('"')[0].split("'")[0].split("\\")[0].split(",")[0].split("]")[0].split("}")[0]
        if url_clean.endswith("&quot;"):
            url_clean = url_clean[:-6]
        if url_clean.endswith("&amp;"):
            url_clean = url_clean[:-5]
            
        # Filter images based on Dola's URL structure patterns
        # High-quality original images typically contain 'raw' or long numeric tokens
        if "avatar" in url_clean.lower() or "icon" in url_clean.lower() or "ratio1_1" in url_clean.lower():
            continue
            
        if "raw" in url_clean.lower():
            raw_images.add(url_clean)
        else:
            if "rc_gen_image" in url_clean.lower():
                other_images.add(url_clean)
            
    return sorted(list(raw_images)), sorted(list(other_images))

@app.post("/parse-thread-images")
async def parse_thread_images(req: ThreadRequest):
    """
    Parse and extract image URLs from Dola thread pages
    
    Args:
        req: ThreadRequest containing share URL and cookie
    
    Returns:
        Dictionary with thread ID, status code, and extracted image URLs
    """
    share_id = extract_share_id(req.shareUrl)
    if not share_id:
        raise HTTPException(status_code=400, detail="Invalid URL or Thread ID")

    if not req.cookie:
        raise HTTPException(status_code=400, detail="Missing cookie configuration from Dola")

    api_url = f"https://www.dola.com/thread/{share_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-EN,en;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cookie": req.cookie,
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        try:
            response = await client.get(api_url, headers=headers)
            raw_html_text = response.text
            
            images_no_watermark, all_variants = harvest_ibyteimg_urls(raw_html_text)
            
            # If raw image array is empty, use bot-generated images (rc_gen_image) as main images
            if not images_no_watermark and all_variants:
                images_no_watermark = all_variants
            
            return {
                "share_id": share_id,
                "status_code_from_dola": response.status_code,
                "images_no_watermark": images_no_watermark,
                "all_variants": {
                    "ibyteimg_other_urls": all_variants
                }
            }
            
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Cannot connect to Dola: {e}")

# Optional: Add root endpoint for health check
@app.get("/")
async def root():
    return {"message": "Dola Thread Image Parser API", "status": "running"}

# Optional: Add endpoint documentation
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
