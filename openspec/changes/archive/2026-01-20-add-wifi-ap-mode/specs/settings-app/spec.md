## ADDED Requirements

### Requirement: WiFi Tab - Access Point Mode
The WiFi tab SHALL allow users to create a WiFi Access Point (hotspot) that other devices can connect to. AP mode and Station mode SHALL be mutually exclusive.

#### Scenario: User switches to AP mode
- **WHEN** user selects AP mode option
- **THEN** station mode SHALL be deactivated if active
- **AND** the AP interface SHALL be activated
- **AND** the UI SHALL display AP status and configuration options

#### Scenario: User opens AP config editor
- **WHEN** user presses E key in AP mode or STA+AP mode
- **THEN** a reusable AP Configuration editor screen SHALL be displayed
- **AND** the editor SHALL show SSID and Password fields in a selectable list

#### Scenario: User edits AP SSID
- **WHEN** user selects SSID field and presses Enter
- **THEN** a text input SHALL allow entering a custom SSID
- **AND** typed characters SHALL be displayed (not masked)

#### Scenario: User edits AP password
- **WHEN** user selects Password field and presses Enter
- **THEN** a text input SHALL allow entering a password (8+ characters for WPA2)
- **AND** typed characters SHALL be masked with asterisks
- **AND** empty password SHALL indicate open network (no security)

#### Scenario: User applies AP config
- **WHEN** user presses A key to apply changes
- **THEN** settings SHALL be saved to NVS namespace "cardputer_wifi"
- **AND** if AP is currently active, it SHALL restart with new settings
- **AND** editor SHALL close and return to previous mode view

#### Scenario: User cancels AP config
- **WHEN** user presses ESC in AP config editor
- **THEN** changes SHALL be discarded
- **AND** editor SHALL close and return to previous mode view

#### Scenario: User starts AP
- **WHEN** user activates the AP
- **AND** SSID is configured
- **THEN** the AP SHALL start with the configured SSID and password
- **AND** the AP IP address (default 192.168.4.1) SHALL be displayed
- **AND** the number of connected clients SHALL be displayed

#### Scenario: User stops AP
- **WHEN** user deactivates the AP
- **THEN** the AP interface SHALL be stopped
- **AND** all connected clients SHALL be disconnected

#### Scenario: User views AP status
- **WHEN** AP is active
- **THEN** the display SHALL show:
  - AP SSID
  - Security type (Open or WPA2)
  - IP address
  - Number of connected clients

### Requirement: WiFi Tab - STA Config Editor
The WiFi tab SHALL provide a reusable STA Configuration editor for scanning and connecting to networks. This editor SHALL be used in both STA mode and STA+AP mode.

#### Scenario: User opens STA config editor from STA mode
- **WHEN** mode is STA
- **THEN** the STA config editor SHALL be displayed as the main view
- **AND** network list, scan, and connect functions SHALL be available

#### Scenario: User opens STA config editor from STA+AP mode
- **WHEN** user presses S key in STA+AP mode
- **THEN** the STA config editor SHALL be displayed
- **AND** ESC SHALL return to the dual mode status view

#### Scenario: User scans for networks
- **WHEN** user presses S key in STA config editor
- **THEN** available networks SHALL be scanned and displayed in a list
- **AND** each network SHALL show SSID, signal strength bars, and security type

#### Scenario: User selects network
- **WHEN** user navigates with up/down keys
- **THEN** the selected network SHALL be highlighted
- **AND** Enter SHALL initiate connection to selected network

#### Scenario: User connects to secured network
- **WHEN** user presses Enter on a secured network (WPA/WPA2)
- **THEN** a password input screen SHALL be displayed
- **AND** typed characters SHALL be masked with asterisks
- **AND** Enter SHALL attempt connection with entered password

#### Scenario: User connects to open network
- **WHEN** user presses Enter on an open network
- **THEN** connection SHALL be attempted immediately without password prompt

#### Scenario: User disconnects
- **WHEN** user presses D key while connected
- **THEN** the station SHALL disconnect from current network

#### Scenario: User exits STA config editor
- **WHEN** user presses ESC in STA config editor
- **AND** mode is STA+AP
- **THEN** editor SHALL close and return to dual mode status view

### Requirement: WiFi Tab - Mode Selection
The WiFi tab SHALL provide mode cycling via the M key through four modes: Off, STA (station), AP (access point), and STA+AP (dual mode).

#### Scenario: User cycles modes with M key
- **WHEN** user presses M key
- **THEN** mode SHALL cycle: Off → STA → AP → STA+AP → Off
- **AND** the mode indicator SHALL update to show current mode

#### Scenario: User switches to Off mode
- **WHEN** mode is set to Off
- **THEN** both station and AP interfaces SHALL be deactivated
- **AND** display SHALL show "WiFi: Off" with prompt to press M to enable

#### Scenario: User switches to STA mode
- **WHEN** mode is set to STA
- **THEN** AP interface SHALL be stopped if active
- **AND** station interface SHALL be activated
- **AND** station mode UI SHALL be displayed (network list, scan, connect)
- **AND** current mode indicator SHALL show "STA"

#### Scenario: User switches to AP mode
- **WHEN** mode is set to AP
- **THEN** station interface SHALL be deactivated if active
- **AND** AP interface SHALL be activated
- **AND** AP mode UI SHALL be displayed (AP config, status)
- **AND** current mode indicator SHALL show "AP"

#### Scenario: User switches to STA+AP mode
- **WHEN** mode is set to STA+AP
- **THEN** both station and AP interfaces SHALL be activated
- **AND** dual mode UI SHALL be displayed showing both interfaces
- **AND** current mode indicator SHALL show "STA+AP"

### Requirement: WiFi Tab - STA+AP Dual Mode
The WiFi tab SHALL support simultaneous station and access point operation in STA+AP mode.

#### Scenario: Dual mode displays both IPs
- **WHEN** STA+AP mode is active
- **AND** station is connected to a network
- **THEN** the display SHALL show the STA IP (assigned by router)
- **AND** the display SHALL show the AP IP (192.168.4.1)

#### Scenario: Dual mode independent operation
- **WHEN** STA+AP mode is active
- **THEN** station connection/disconnection SHALL NOT affect AP
- **AND** AP start/stop SHALL NOT affect station connection

#### Scenario: Dual mode status display
- **WHEN** STA+AP mode is active
- **THEN** the display SHALL show:
  - STA status (connected SSID or "Not connected")
  - STA IP address (if connected)
  - AP SSID and security type
  - AP IP address (192.168.4.1)
  - Number of AP clients connected

### Requirement: WiFi Tab - AP Settings Persistence
The WiFi tab SHALL persist AP configuration and mode selection to NVS for restoration.

#### Scenario: AP settings saved
- **WHEN** user configures AP SSID or password
- **THEN** settings SHALL be saved to NVS namespace "cardputer_wifi"
- **AND** settings SHALL persist across device reboots

#### Scenario: Mode selection saved
- **WHEN** user changes WiFi mode (Off, STA, AP, or STA+AP)
- **THEN** the mode SHALL be saved to NVS namespace "cardputer_wifi" key "mode"
- **AND** mode SHALL persist across device reboots

#### Scenario: AP settings loaded
- **WHEN** WiFi tab is opened
- **THEN** saved AP SSID, password, and mode SHALL be loaded from NVS
- **AND** fields SHALL be pre-populated with saved values
- **AND** the saved mode SHALL be restored

#### Scenario: Default AP SSID
- **WHEN** no AP SSID is configured
- **THEN** the default SSID SHALL be "Cardputer-AP"

#### Scenario: Default mode
- **WHEN** no mode is saved
- **THEN** the default mode SHALL be STA (station)

### Requirement: WiFi Boot Initialization
The boot process SHALL restore WiFi mode and connections based on saved NVS settings.

#### Scenario: Boot with mode Off
- **WHEN** device boots
- **AND** saved mode is Off (0)
- **THEN** no WiFi interfaces SHALL be activated

#### Scenario: Boot with mode STA
- **WHEN** device boots
- **AND** saved mode is STA (1)
- **AND** STA credentials are saved
- **THEN** station interface SHALL be activated
- **AND** connection to saved network SHALL be attempted

#### Scenario: Boot with mode AP
- **WHEN** device boots
- **AND** saved mode is AP (2)
- **THEN** AP interface SHALL be activated
- **AND** AP SHALL start with saved SSID and password

#### Scenario: Boot with mode STA+AP
- **WHEN** device boots
- **AND** saved mode is STA+AP (3)
- **THEN** both interfaces SHALL be activated
- **AND** STA connection SHALL be attempted if credentials exist
- **AND** AP SHALL start with saved settings

#### Scenario: Boot with no saved credentials
- **WHEN** device boots with STA or STA+AP mode
- **AND** no STA credentials are saved
- **THEN** STA interface SHALL be activated but not connected
- **AND** AP SHALL still start if mode includes AP
