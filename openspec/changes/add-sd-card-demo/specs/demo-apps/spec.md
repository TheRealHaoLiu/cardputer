## ADDED Requirements

### Requirement: SD Card Demo

The SD card demo SHALL demonstrate microSD card operations using `machine.SDCard` with the Cardputer ADV pin configuration (SCK:40, MISO:39, MOSI:14, CS:12).

#### Scenario: SD card mount success

- **WHEN** user launches SD card demo
- **AND** a FAT32 formatted microSD card is inserted
- **THEN** the demo SHALL mount the SD card to `/sd`
- **AND** display the SD card information and root directory contents

#### Scenario: SD card not present

- **WHEN** user launches SD card demo
- **AND** no microSD card is inserted or mount fails
- **THEN** the demo SHALL display a clear error message
- **AND** show instructions for inserting a card (contacts facing away from screen)

#### Scenario: SD card information display

- **WHEN** SD card is mounted
- **THEN** the demo SHALL display card information using `os.statvfs()`:
  - Total capacity in MB
  - Used space in MB
  - Free space in MB
  - Usage percentage bar or indicator

#### Scenario: Directory listing with file info

- **WHEN** SD card is mounted
- **THEN** the demo SHALL display files and folders with:
  - Name (truncated if too long for screen)
  - Size in bytes/KB/MB (for files)
  - Type indicator (folder icon or [DIR] marker)

#### Scenario: Directory navigation

- **WHEN** user presses up/down keys
- **THEN** the demo SHALL scroll through the file/directory listing
- **WHEN** user presses Enter on a directory
- **THEN** the demo SHALL enter that directory and show its contents
- **WHEN** user presses Backspace
- **THEN** the demo SHALL navigate to the parent directory

#### Scenario: Text file viewing

- **WHEN** user selects a text file and presses Enter
- **THEN** the demo SHALL display the file contents on screen
- **AND** support scrolling for files longer than the display

#### Scenario: File creation

- **WHEN** user presses the write key (W)
- **THEN** the demo SHALL create a test file named `cardputer_test.txt`
- **AND** write the current timestamp and a test message
- **AND** display a success confirmation
- **AND** refresh the directory listing to show the new file

#### Scenario: App exit cleanup

- **WHEN** user exits the demo (ESC key)
- **THEN** the demo SHALL close any open file handles
- **AND** unmount the SD card using `os.umount('/sd')`
- **AND** deinitialize the SDCard object to release the SPI bus
- **AND** handle errors gracefully if card was already removed
