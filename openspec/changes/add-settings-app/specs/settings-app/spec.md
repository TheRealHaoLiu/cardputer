## ADDED Requirements

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
The WiFi tab SHALL allow users to enable or disable the WiFi radio.

#### Scenario: User disables WiFi
- **WHEN** user toggles WiFi to OFF
- **THEN** the WiFi radio SHALL be deactivated
- **AND** network list SHALL be cleared
- **AND** connection info SHALL show "Disabled"

#### Scenario: User enables WiFi
- **WHEN** user toggles WiFi to ON
- **THEN** the WiFi radio SHALL be activated
- **AND** auto-reconnect to saved network SHALL be attempted

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
