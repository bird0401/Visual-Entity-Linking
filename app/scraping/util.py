from tenacity import retry, stop_after_attempt, wait_exponential
import requests
from requests.exceptions import Timeout
import time
import traceback
from fake_useragent import UserAgent

def ToAbsURL(base_url = 'https://commons.wikimedia.org', related_url = '/wiki/Category'):
  return base_url+related_url

ua = UserAgent()
header = {'user-agent':ua.chrome}
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
def Fetch(url):
  try: 
    res = requests.get(url, headers=header, timeout=10)
  except Timeout:
    print('Timeout has been raised.')
    return None
  except Exception:
    traceback.print_exc()
    return None
  time.sleep(1) 
  return res