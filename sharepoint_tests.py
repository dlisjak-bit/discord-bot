from requests_ntlm import HttpNtlmAuth
import requests
from io import BytesIO

auth = HttpNtlmAuth(username = username,
                     password = password)
 
responseObject = requests.get(url, auth = auth)

file = BytesIO(responseObject.content)
df = pd.read_excel(file)