# Bug: FTP Server Auth Toggle Inverted

## Summary

The FTP server's authentication toggle has inverted behavior - when auth is enabled, anonymous access works, and when auth is disabled, credentials are required.

## Steps to Reproduce

1. Launch FTP Server app
2. Press 'A' to toggle auth ON
3. Try to connect anonymously → **Works** (should fail)
4. Press 'A' to toggle auth OFF
5. Try to connect anonymously → **Fails** (should work)

## Expected Behavior

- Auth ON: Require username/password, reject anonymous
- Auth OFF: Allow anonymous access

## Actual Behavior

- Auth ON: Anonymous access allowed
- Auth OFF: Credentials required (times out on anonymous)

## Affected File

`apps/ftp_server.py` - likely the auth check logic is inverted

## Discovered

2026-01-22 during poe ftp-upload testing
