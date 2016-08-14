# Memebot
Memebot is a bare-bones Slackbot written in Python.  It has two main functions: uploading stupid images on demand and updating a spotify playlist with songs the group requests.

To get started, just copy slackbot.py on your machine/a VM, insert your slack bot user API token, your spotify OAuth tokens, and the IDs of your Slack channels to monitor. If you want it to post random pics on demand, make sure to have a folder full o' pics handy for it to reference in __main__.

FAQ:

## Why not build off of Slack's boilerplate bot API?

This was the path of least resistance. I had cobbled together most of the code already as proof-of-concepts for programmatically using the API on a Saturday afternoon.  Was ready to let the beast create havoc in slack and put my keyboard away.

## What do you plan on adding?

a vote system to remove songs from the playlist so you can remove the troll songs your clever friend adds to the playlist. Migrating the functionality to plugins for Slack's bot framework instead of a single Python script.
