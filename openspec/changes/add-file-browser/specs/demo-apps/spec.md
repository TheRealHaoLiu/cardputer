# demo-apps Specification Delta

## REMOVED Requirements

### Requirement: SD Card Demo

The SD Card Demo requirement is removed and superseded by the `file-browser` capability specification.

#### Scenario: Superseded by file-browser

- **WHEN** the add-file-browser change is applied
- **THEN** the SD Card Demo requirement SHALL be removed from demo-apps
- **AND** the file-browser spec SHALL be the source of truth for file browsing functionality

**Reason:** The file browser generalizes SD card browsing to support multiple storage locations (/flash, /sd, /system), making the SD-card-specific requirements obsolete.

**See:** `openspec/specs/file-browser/spec.md` for the replacement requirements.
