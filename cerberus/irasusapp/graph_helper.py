import requests
import json

graph_url = 'https://graph.microsoft.com/v1.0'

def get_user(token):
    # Send GET to /me
    user = requests.get('{0}/me'.format(graph_url),
    headers={'Authorization': 'Bearer {0}'.format(token)},
    params={
'$select':'displayName,mail,mailboxSettings,userPrincipalName'})
    return user.json()