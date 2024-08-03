from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.http import HttpResponse
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import requests
import jwt
from .summary import summarize
# Create your views here.

from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/userinfo.profile']

@login_required
@cache_control(no_cache=True, must_revalidate=True,no_store=True)
def index(request):
    if request.method == 'POST':
        # authorization_response = request.build_absolute_uri()
        # authorization_url, state = start_oauth_flow()
        # logger.debug('Made It.')
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES)
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

        request.session['state'] = state
        return redirect(authorization_url)
    else:
        return render(request,'index.html')

# @cache_control(no_cache=True, must_revalidate=True,no_store=True)

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def callback(request):
    state = request.session.get('state')
    if not state:
        return HttpResponse("ERROR! Not allowed.", status=400)

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    authorization_response = request.build_absolute_uri()
    
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except Exception as e:
        return HttpResponse(f"Error fetching token: {str(e)}", status=400)
    
    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)

    return redirect('emails')

def emails(request):
    #didn't provide proper credentials
    if 'credentials' not in request.session:
        return redirect('callback')

    credentials = google.oauth2.credentials.Credentials(
        **request.session['credentials']
    )

    service = googleapiclient.discovery.build('gmail', 'v1', credentials=credentials)

    # Call the Gmail API to fetch the user's emails
    search_query = 'subject:receipt OR subject:invoice'
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10, q=search_query).execute()

    messages = results.get('messages', [])

    email_list = []
    
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        email_list.append({
            'snippet': msg['snippet'],
            'id': msg['id']})

    # Update the session credentials
    request.session['credentials'] = credentials_to_dict(credentials)
    # added
    request.session['emails'] = email_list

    return render(request, 'emails.html', {'emails': email_list})

def summ(request):
    email_list = request.session.get('emails')
    summarized = []
    for email in email_list:
        summarized.append(summarize(email['snippet']))
    return render(request, 'emails.html', {'emails': email_list,'summarized':summarized})