# reset win rate
import requests
URL = "http://upe.42069.fun/UE0XI/reset"
data = {"email":"stevenla@g.ucla.edu"}
r = requests.post(URL,data)
print (r.json())