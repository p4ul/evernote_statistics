import json
import cosm
import hashlib
import binascii
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
import evernote.edam.notestore.ttypes as NoteTypes
from datetime import datetime
from evernote.api.client import EvernoteClient
import ConfigParser


config = ConfigParser.ConfigParser()
config.read('config.cfg')

# print config.items('API_KEYS')
# for k in config.items('API_KEYS'):
# 	print k[0]

# exit(1)

api_evernote= config.get('API_KEYS','evernote_auth_token')
api_cosm = config.get('API_KEYS','cosm_api_key')

cosm_feed_id_or_url = config.get('COSM','cosm_feed_id_or_url')


if api_evernote == "your developer token":
    print "Please fill in your developer token"
    print "To get a developer token, visit " \
        "https://www.evernote.com/api/DeveloperToken.action"
    exit(1)

cosm_api = cosm.CosmAPIClient(api_cosm)


print "getting feed: ", cosm_feed_id_or_url
feed = cosm_api.feeds.get(cosm_feed_id_or_url)


# Initial development is performed on our sandbox server. To use the production
# service, change sandbox=False and replace your
# developer token above with a token from
# https://www.evernote.com/api/DeveloperToken.action
client = EvernoteClient(token=api_evernote, sandbox=False)
user_store = client.get_user_store()

version_ok = user_store.checkVersion(
    "Evernote EDAMTest (Python)",
    UserStoreConstants.EDAM_VERSION_MAJOR,
    UserStoreConstants.EDAM_VERSION_MINOR
)
print "Is my Evernote API version up to date? ", str(version_ok)
print ""
if not version_ok:
    exit(1)


note_store = client.get_note_store()


f = NoteTypes.NoteFilter()
noteBookCounts = note_store.findNoteCounts(f, True)


tasks_stack = 0
other_stack = 0
action_pending = 0
completed = 0

for notebook_guid in noteBookCounts.notebookCounts:
    notebook = note_store.getNotebook(notebook_guid)
    print notebook.stack, ' ', notebook.name, noteBookCounts.notebookCounts[notebook_guid]
    
    if notebook.stack == '_old' and notebook.name != 'Complete':
        continue

    if notebook.name == 'Action Pending' :
        action_pending += noteBookCounts.notebookCounts[notebook_guid]

    if notebook.stack == 'Tasks' :
        tasks_stack += noteBookCounts.notebookCounts[notebook_guid]
    elif notebook.name == 'Complete' :
        completed += noteBookCounts.notebookCounts[notebook_guid]
    else :
        other_stack += noteBookCounts.notebookCounts[notebook_guid]

    
print tasks_stack, 'tasks stack'
print completed, 'complete'
print action_pending, 'action pending'
print other_stack, 'other stack'



cosm_datastream = feed.datastreams.get("action_pending")
cosm_datastream.current_value = action_pending
cosm_datastream.update(fields=['current_value'])

cosm_datastream = feed.datastreams.get("tasks")
cosm_datastream.current_value = tasks_stack
cosm_datastream.update(fields=['current_value'])


cosm_datastream = feed.datastreams.get("complete")
cosm_datastream.current_value =completed
cosm_datastream.update(fields=['current_value'])

cosm_datastream = feed.datastreams.get("other")
cosm_datastream.current_value =other_stack
cosm_datastream.update(fields=['current_value'])

cosm_datastream = feed.datastreams.get("trashed")
cosm_datastream.current_value = noteBookCounts.trashCount
cosm_datastream.update(fields=['current_value'])

