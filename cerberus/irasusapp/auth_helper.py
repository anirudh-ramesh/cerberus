import msal
import json


# logging.getLogger("msal").setLevel(logging.WARN)
credential = json.load(open('microsoft_config.json', 'r'))
scopes = credential['scopes']

def loadCache(request):
  # Check for a token cache in the session
  cache = msal.SerializableTokenCache()
  if request.session.get('token_cache'):
    cache.deserialize(request.session['token_cache'])
  return cache


def saveCache(request, cache):
  # If cache has changed, persist back to session
  if cache.has_state_changed:
    request.session['token_cache'] = cache.serialize()

def getMsalApp(cache=None):
  # Initialize the MSAL confidential client
  auth_app = msal.ConfidentialClientApplication(
    credential['app_id'],
    authority=credential['authority'],
    client_credential=credential['app_secret'],
    token_cache=cache)
  return auth_app


def getSignInFlow():
  auth_app = getMsalApp()
  return auth_app.initiate_auth_code_flow(
    scopes,
    redirect_uri=credential['redirect'])


def getTokenFromCode(request):
  cache = loadCache(request)
  auth_app = getMsalApp(cache)

    # Get the flow saved in session
  flow = request.session.pop('auth_flow', {})
  result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)
  saveCache(request, cache)

  return result


def storeUser(request, user):
  try:
    request.session['user'] = {
      'is_authenticated': True,
      'name': user['displayName'],
      'email': user['mail'] if (user['mail'] != None) else user['userPrincipalName'],
      'timeZone': user['mailboxSettings']['timeZone'] if (user['mailboxSettings']['timeZone'] != None) else 'UTC'
    }
  except Exception as e:
    print(e)

def getToken(request):
  cache = loadCache(request)
  auth_app = getMsalApp(cache)
  accounts = auth_app.get_accounts()
  if accounts:
    result = auth_app.acquire_token_silent(
      scopes,
      account=accounts[0])
    saveCache(request, cache)

    return result['access_token']

def removeUserAndToken(request):
  if 'token_cache' in request.session:
    del request.session['token_cache']

  if 'user' in request.session:
    del request.session['user']
