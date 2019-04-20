#!/usr/bin/env python3

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import os
import sys
import glob
import json

from github3 import login

name_prefix = f'travis-{os.environ["TRAVIS_BUILD_ID"]}-'
label_prefix = f'/travis/{os.environ["TRAVIS_BUILD_ID"]}/'

gh = login(token=os.getenv('GITHUB_TOKEN'))
repo = repo = gh.repository("retorquere", "zotero-better-bibtex")
release = repo.release_from_tag('builds')

action = sys.argv[1]
if action not in ['stash', 'fetch', 'pop']:
  print(f'Unexpected action {json.dumps(action)}')
  sys.exit(1)

generated = [
  'gen/translators.json',
  'gen/preferences/defaults.json',
]

for asset in release.assets():
  if not asset.label.startswith(label_prefix): continue
 
  if action == 'fetch':
    filename = asset.label[len(label_prefix):]
    print(f'Downloading {asset.label}')
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
      asset.download(f)
  else:
    print(f'Removing {asset.label}')
    asset.delete()

if action == 'stash':
  for asset in glob.glob('xpi/*.xpi') + generated:
    print(f'Uploading {asset}')
    with open(asset, 'rb') as f:
      release.upload_asset(
        asset=f,
        name=name_prefix + os.path.basename(asset),
        label=label_prefix + asset,
        content_type=('application/x-xpinstall' if asset.endswith('.xpi') else 'application/json')
      )
