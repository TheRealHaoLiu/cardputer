# settings-app Specification

## Purpose
TBD - created by archiving change add-settings-app. Update Purpose after archive.
## Requirements
### Requirement: Settings App Structure
The Settings App SHALL provide a tabbed interface for configuring device settings. Users SHALL navigate between tabs using the Tab key.

#### Scenario: User navigates between tabs
- **WHEN** user presses Tab key
- **THEN** the next tab SHALL become active
- **AND** the tab bar SHALL visually indicate the active tab
- **AND** the tab content area SHALL display the new tab's content

#### Scenario: User reverse navigates tabs
- **WHEN** user presses Shift+Tab
- **THEN** the previous tab SHALL become active

#### Scenario: User exits settings
- **WHEN** user presses ESC from any tab
- **THEN** the Settings App SHALL exit to the launcher

### Requirement: WiFi Tab - Network Scanning
The WiFi tab SHALL scan for available wireless networks and display them in a list with signal strength indicators.

#### Scenario: User scans for networks
- **WHEN** user triggers a network scan
- **THEN** available networks SHALL be displayed in a scrollable list
- **AND** each network SHALL show SSID, signal strength bars, and security type

#### Scenario: Signal strength display
- **WHEN** a network has RSSI > -50 dBm
- **THEN** 4 signal bars SHALL be displayed
- **WHEN** a network has RSSI > -60 dBm
- **THEN** 3 signal bars SHALL be displayed
- **WHEN** a network has RSSI > -70 dBm
- **THEN** 2 signal bars SHALL be displayed
- **WHEN** a network has RSSI <= -70 dBm
- **THEN** 1 signal bar SHALL be displayed

### Requirement: WiFi Tab - Network Connection
The WiFi tab SHALL allow users to connect to selected networks by entering credentials.

#### Scenario: User connects to secured network
- **WHEN** user selects a secured network (WPA/WPA2/WPA3)
- **THEN** a password input prompt SHALL be displayed
- **AND** typed characters SHALL be masked
- **WHEN** user presses Enter after entering password
- **THEN** connection SHALL be attempted
- **AND** success or failure status SHALL be displayed

#### Scenario: User connects to open network
- **WHEN** user selects an open network
- **THEN** connection SHALL be attempted immediately without password prompt

### Requirement: WiFi Tab - Hidden Network
The WiFi tab SHALL allow users to manually enter credentials for hidden networks.

#### Scenario: User adds hidden network
- **WHEN** user selects "Add hidden network" option
- **THEN** SSID text input SHALL be displayed
- **AND** password text input SHALL be displayed
- **WHEN** user enters credentials and confirms
- **THEN** connection SHALL be attempted to the hidden network

### Requirement: WiFi Tab - Connection Information
The WiFi tab SHALL display detailed connection information when connected to a network.

#### Scenario: User views connection info
- **WHEN** device is connected to a network
- **THEN** the display SHALL show IP address
- **AND** MAC address
- **AND** gateway address
- **AND** subnet mask
- **AND** DNS server
- **AND** signal strength (RSSI) with bars
- **AND** WiFi channel number

### Requirement: WiFi Tab - Hostname Configuration
The WiFi tab SHALL allow users to configure the device hostname.

#### Scenario: User changes hostname
- **WHEN** user edits the hostname field
- **AND** enters a new hostname
- **THEN** the hostname SHALL be saved to NVS
- **AND** the device SHALL use the new hostname for network identification

#### Scenario: Default hostname
- **WHEN** no hostname is configured
- **THEN** the default hostname SHALL be "cardputer"

### Requirement: WiFi Tab - WiFi Toggle
The WiFi tab SHALL allow users to enable or disable the WiFi radio. The WiFi state SHALL be persisted to NVS and restored on boot.

#### Scenario: User disables WiFi
- **WHEN** user toggles WiFi to OFF
- **THEN** the WiFi radio SHALL be deactivated
- **AND** network list SHALL be cleared
- **AND** connection info SHALL show "Disabled"
- **AND** wifi_on SHALL be set to 0 in NVS

#### Scenario: User enables WiFi
- **WHEN** user toggles WiFi to ON
- **THEN** the WiFi radio SHALL be activated
- **AND** wifi_on SHALL be set to 1 in NVS

#### Scenario: WiFi state persists
- **WHEN** user toggles WiFi state
- **AND** device is rebooted
- **THEN** the WiFi state SHALL match the saved setting

### Requirement: WiFi Tab - Credential Persistence
The WiFi tab SHALL save network credentials to NVS for automatic reconnection.

#### Scenario: Credentials saved on successful connection
- **WHEN** user successfully connects to a network
- **THEN** the SSID and password SHALL be saved to NVS namespace "wifi"
- **AND** these credentials SHALL persist across device reboots

#### Scenario: User connects to saved network
- **WHEN** saved credentials exist
- **AND** user presses C key
- **THEN** connection SHALL be attempted using saved credentials

#### Scenario: User forgets saved network
- **WHEN** user presses F key
- **THEN** saved credentials SHALL be erased from NVS
- **AND** the saved network indicator SHALL be removed from display

### Requirement: WiFi Tab - QR Code Sharing
The WiFi tab SHALL generate a QR code for sharing current network credentials.

#### Scenario: User generates WiFi QR code
- **WHEN** user selects QR share option while connected
- **THEN** a QR code SHALL be displayed encoding the WiFi credentials
- **AND** the QR code SHALL use the format "WIFI:T:WPA;S:<ssid>;P:<password>;;"
- **WHEN** user presses any key
- **THEN** the display SHALL return to normal WiFi tab view

### Requirement: Display Tab - Brightness Control
The Display tab SHALL provide brightness adjustment with visual feedback.

#### Scenario: User adjusts brightness
- **WHEN** user presses left/right arrow or +/- keys
- **THEN** brightness SHALL change by increment of 10
- **AND** the slider bar SHALL update in real-time
- **AND** the screen brightness SHALL change immediately

#### Scenario: User uses brightness preset
- **WHEN** user presses 1, 2, 3, or 4 key
- **THEN** brightness SHALL be set to 25%, 50%, 75%, or 100% respectively

#### Scenario: User turns off screen
- **WHEN** user presses 0 key
- **THEN** screen brightness SHALL be set to 0 (off)
- **WHEN** user presses any key while screen is off
- **THEN** screen brightness SHALL be restored to previous value

#### Scenario: User saves brightness
- **WHEN** user presses S key
- **THEN** current brightness SHALL be saved to NVS key "brightness"

### Requirement: Sound Tab - Volume Control
The Sound tab SHALL provide volume adjustment with audio feedback.

#### Scenario: User adjusts volume
- **WHEN** user presses left/right arrow or +/- keys
- **THEN** volume SHALL change by increment
- **AND** a feedback tone (440Hz, 50ms) SHALL play at the new volume
- **AND** the slider bar SHALL update in real-time

#### Scenario: User mutes audio
- **WHEN** user presses M key
- **THEN** audio SHALL be muted
- **AND** mute indicator SHALL be displayed
- **WHEN** user presses M key again
- **THEN** audio SHALL be unmuted to previous volume

#### Scenario: User tests audio
- **WHEN** user presses T key
- **THEN** a test tone SHALL play for 500ms

#### Scenario: User saves volume
- **WHEN** user presses S key
- **THEN** current volume SHALL be saved to NVS key "volume"

### Requirement: System Tab - Boot Option
The System tab SHALL allow configuration of device boot behavior.

#### Scenario: User changes boot option
- **WHEN** user cycles through boot options
- **THEN** options SHALL include: "Run main.py", "Show Launcher", "Setup Mode"
- **AND** selection SHALL be saved to NVS key "boot_option" immediately

### Requirement: System Tab - System Information
The System tab SHALL display memory and storage statistics.

#### Scenario: User views system info
- **WHEN** user is on System tab
- **THEN** free and total heap memory SHALL be displayed
- **AND** flash storage usage SHALL be displayed

### Requirement: System Tab - Reboot
The System tab SHALL allow device restart.

#### Scenario: User reboots device
- **WHEN** user selects reboot option
- **THEN** a confirmation prompt SHALL be displayed
- **WHEN** user confirms
- **THEN** device SHALL perform soft reset

### Requirement: About Tab - Device Information
The About tab SHALL display device and firmware information.

#### Scenario: User views about info
- **WHEN** user is on About tab
- **THEN** device model SHALL be displayed
- **AND** chip information (ESP32-S3) SHALL be displayed
- **AND** MicroPython version SHALL be displayed
- **AND** MAC address SHALL be displayed
- **AND** uptime since boot SHALL be displayed
- **AND** battery level percentage SHALL be displayed
- **AND** charging status SHALL be indicated when plugged in

#### Scenario: Battery level color indication
- **WHEN** battery level is above 50%
- **THEN** level SHALL be displayed in green
- **WHEN** battery level is between 20% and 50%
- **THEN** level SHALL be displayed in yellow
- **WHEN** battery level is below 20%
- **THEN** level SHALL be displayed in red

### Requirement: WiFi Boot Connect
The system SHALL automatically connect to WiFi on boot when WiFi is enabled and credentials are saved.

#### Scenario: Auto-connect on boot with saved credentials
- **WHEN** the device boots
- **AND** WiFi is enabled (wifi_on = 1 in NVS)
- **AND** credentials are saved in NVS
- **THEN** the system SHALL attempt to connect to the saved network

#### Scenario: No connect when WiFi disabled
- **WHEN** the device boots
- **AND** WiFi is disabled (wifi_on = 0 in NVS)
- **THEN** the system SHALL NOT attempt to connect to WiFi

#### Scenario: No connect when no credentials
- **WHEN** the device boots
- **AND** WiFi is enabled
- **AND** no credentials are saved
- **THEN** the system SHALL NOT attempt to connect

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

