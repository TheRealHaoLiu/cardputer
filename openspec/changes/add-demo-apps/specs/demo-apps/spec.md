## ADDED Requirements

### Requirement: Demo App Structure
Each demo app SHALL inherit from `AppBase` and implement the standard lifecycle methods. Demo apps MUST be placed in the `apps/` directory for auto-discovery by the launcher.

#### Scenario: Demo app is discovered by launcher
- **WHEN** a demo app file exists in `apps/` directory
- **AND** it exports an `App` class inheriting from `AppBase`
- **THEN** the launcher SHALL display it in the app menu

#### Scenario: Demo app handles ESC key
- **WHEN** user presses ESC in a demo app
- **THEN** the app SHALL return control to the launcher

### Requirement: Sound Demo
The sound demo SHALL demonstrate the Speaker hardware capabilities including tone generation and volume control.

#### Scenario: User generates tones
- **WHEN** user navigates to sound demo
- **AND** user presses keys to adjust frequency
- **THEN** the speaker SHALL play tones at the selected frequency

#### Scenario: User adjusts volume
- **WHEN** user presses volume up/down keys
- **THEN** the speaker volume SHALL change accordingly
- **AND** the current volume level SHALL be displayed on screen

### Requirement: Shapes Demo
The shapes demo SHALL demonstrate LCD drawing capabilities for geometric primitives.

#### Scenario: User views shape gallery
- **WHEN** user navigates through shapes demo
- **THEN** the display SHALL show various geometric shapes (lines, circles, rectangles, triangles, arcs)

#### Scenario: User cycles through shapes
- **WHEN** user presses navigation keys
- **THEN** the demo SHALL display different shape types or variations

### Requirement: QR Code Demo
The QR code demo SHALL demonstrate the LCD's ability to generate and display QR codes.

#### Scenario: User views QR codes
- **WHEN** user is in QR code demo
- **THEN** the display SHALL show a generated QR code
- **AND** the encoded content SHALL be displayed as text

### Requirement: Storage Demo
The storage demo SHALL demonstrate NVS (Non-Volatile Storage) for persistent data.

#### Scenario: User increments persistent counter
- **WHEN** user presses a key to increment counter
- **THEN** the counter value SHALL be stored in NVS
- **AND** the value SHALL persist across device reboots

### Requirement: System Info Demo
The system info demo SHALL display ESP32-S3 system information.

#### Scenario: User views system information
- **WHEN** user opens system info demo
- **THEN** the display SHALL show memory usage (free/used)
- **AND** chip information
- **AND** flash filesystem statistics

### Requirement: WiFi Scanner Demo
The WiFi scanner demo SHALL scan and display nearby wireless networks.

#### Scenario: User scans for networks
- **WHEN** user initiates a WiFi scan
- **THEN** the display SHALL list discovered networks
- **AND** each entry SHALL show SSID, signal strength, and security type

### Requirement: Snake Game Demo
The snake game demo SHALL provide a playable implementation of the classic Snake game.

#### Scenario: User plays snake game
- **WHEN** user starts snake game
- **THEN** the game SHALL render a snake on a game board
- **AND** keyboard controls SHALL move the snake
- **AND** eating food SHALL grow the snake
- **AND** collision with walls or self SHALL end the game

### Requirement: Piano Demo
The piano demo SHALL turn the Cardputer keyboard into a musical instrument.

#### Scenario: User plays musical notes
- **WHEN** user presses keyboard keys
- **THEN** corresponding musical notes SHALL play through the speaker
- **AND** visual feedback SHALL indicate which note is playing
