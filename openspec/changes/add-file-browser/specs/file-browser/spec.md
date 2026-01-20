# file-browser Specification

## Purpose

Provide a read-only file browser for exploring device storage locations including internal flash, microSD card, and system firmware files.

## ADDED Requirements

### Requirement: Storage Location Selection

The file browser SHALL present a root selector menu on launch allowing users to choose which storage location to browse.

#### Scenario: Root selector display

- **WHEN** user launches the file browser
- **THEN** the browser SHALL display a menu with available storage locations:
  - `/flash` - Internal flash storage (always available)
  - `/sd` - MicroSD card (availability checked)
  - `/system` - System/firmware files (always available)
- **AND** indicate if a storage location is unavailable (e.g., no SD card)

#### Scenario: SD card availability check

- **WHEN** the root selector is displayed
- **THEN** the browser SHALL check if an SD card is present
- **AND** display "(no card)" or similar indicator if mount fails
- **AND** allow selection only of available storage locations

#### Scenario: Storage location selection

- **WHEN** user selects a storage location from the root selector
- **THEN** the browser SHALL navigate to that location's root directory
- **AND** display the directory contents

### Requirement: Storage Location Navigation

The file browser SHALL allow users to navigate between storage locations without restarting the app.

#### Scenario: Return to root selector

- **WHEN** user is at the root of a storage location (e.g., `/flash`)
- **AND** user presses Backspace
- **THEN** the browser SHALL return to the root selector menu
- **AND** unmount SD card if it was previously mounted

#### Scenario: Navigate within storage

- **WHEN** user is browsing within a storage location
- **THEN** navigation SHALL work as before (Up/Down to select, Enter to open, Backspace to go up)
- **AND** the current path SHALL be shown in the title bar

### Requirement: Storage Information Display

The file browser SHALL display storage capacity information for each browsable location.

#### Scenario: Storage info for flash

- **WHEN** user is browsing `/flash`
- **AND** user presses the Info key (I)
- **THEN** the browser SHALL display flash storage statistics:
  - Total capacity in MB
  - Used space in MB
  - Free space in MB
  - Usage percentage bar

#### Scenario: Storage info for SD card

- **WHEN** user is browsing `/sd`
- **AND** user presses the Info key (I)
- **THEN** the browser SHALL display SD card statistics using `os.statvfs()`

#### Scenario: Storage info for system

- **WHEN** user is browsing `/system`
- **AND** user presses the Info key (I)
- **THEN** the browser SHALL display system storage statistics if available
- **OR** display "Info not available" if statvfs fails on this mount

### Requirement: Directory Browsing

The file browser SHALL provide directory navigation for any storage location.

#### Scenario: Directory listing

- **WHEN** user is browsing a directory
- **THEN** the browser SHALL display files and folders with:
  - Name (truncated if too long for screen)
  - Size in bytes/KB/MB (for files)
  - Visual distinction between files and directories (color/suffix)

#### Scenario: Enter subdirectory

- **WHEN** user selects a directory and presses Enter
- **THEN** the browser SHALL enter that directory
- **AND** display its contents

#### Scenario: Navigate up

- **WHEN** user presses Backspace
- **AND** user is not at the storage root
- **THEN** the browser SHALL navigate to the parent directory

### Requirement: Text File Viewing

The file browser SHALL display text file contents in a scrollable viewer.

#### Scenario: Open text file

- **WHEN** user selects a file and presses Enter
- **THEN** the browser SHALL attempt to read and display the file contents
- **AND** support scrolling with Up/Down keys
- **AND** support horizontal scrolling with Left/Right keys for long lines

#### Scenario: Binary file handling

- **WHEN** user opens a file that cannot be decoded as text
- **THEN** the browser SHALL display "(binary file - cannot display)"

#### Scenario: Large file handling

- **WHEN** user opens a file with more than 100 lines
- **THEN** the browser SHALL read only the first 100 lines

### Requirement: Read-Only Operation

The file browser SHALL be read-only with no file modification capabilities.

#### Scenario: No write operations

- **WHEN** user is browsing any storage location
- **THEN** no keys SHALL create, modify, or delete files
- **AND** the R key SHALL only refresh the directory listing
