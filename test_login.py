import urllib.request
import urllib.error
import uuid

boundary = uuid.uuid4().hex
data = f'--{boundary}\r\nContent-Disposition: form-data; name="email"\r\n\r\nadmin@smartworklife.com\r\n--{boundary}\r\nContent-Disposition: form-data; name="password"\r\n\r\nAdminSmartWorkLife2025!\r\n--{boundary}--\r\n'.encode('utf-8')

req = urllib.request.Request('https://smartworklifedev.vercel.app/admin/login', data=data, headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
try:
    print(urllib.request.urlopen(req).read().decode())
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode())
