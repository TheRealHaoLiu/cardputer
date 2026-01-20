# Launcher

The home screen app that displays available apps and lets users launch them.

## ADDED Requirements

### Requirement: Lazy App Loading

The launcher SHALL display apps without importing their modules. Apps SHALL be loaded only when the user selects them.

#### Scenario: Menu displays without imports
- **WHEN** the launcher becomes active (boot or ESC return)
- **THEN** the menu displays app names from manifest.json files
- **AND** no app modules are imported

#### Scenario: App loads on selection
- **WHEN** the user presses Enter on an app
- **THEN** the app module is imported and instantiated
- **AND** the app is launched

#### Scenario: Loaded apps are cached
- **WHEN** the user launches an app that was previously loaded
- **THEN** the cached instance is used
- **AND** no reimport occurs

### Requirement: Launcher Exclusion

The launcher itself SHALL never appear in the app menu.

#### Scenario: Launcher excluded from menu
- **WHEN** scanning for apps
- **THEN** `launcher.py` is excluded from the menu
- **AND** users cannot launch the launcher from within the launcher

### Requirement: Display Names from Manifest

The launcher SHALL read display names from `manifest.json` files in each directory.

#### Scenario: Load manifest
- **WHEN** scanning a directory for apps
- **THEN** the `manifest.json` file is loaded
- **AND** app display names are read from the JSON object

#### Scenario: Manifest format
- **GIVEN** a `manifest.json` file
- **THEN** it contains a JSON object mapping module names to display names
- **EXAMPLE** `{"hello_world": "Hello World", "sound_demo": "Sound Demo"}`

#### Scenario: Missing manifest
- **WHEN** a directory does not contain a `manifest.json`
- **THEN** the directory is skipped (no apps loaded from it)

### Requirement: Hierarchical Menu Structure

The launcher SHALL support hierarchical menus based on directory structure.

#### Scenario: Subdirectories become submenus
- **WHEN** the `apps/` directory contains a subdirectory (e.g., `apps/demo/`)
- **AND** the subdirectory contains a `manifest.json`
- **THEN** the subdirectory appears as a submenu item in the launcher
- **AND** the display name is derived from the directory name (e.g., "Demo")

#### Scenario: Enter submenu
- **WHEN** the user presses Enter on a submenu item
- **THEN** the menu displays the contents of that subdirectory
- **AND** apps and nested submenus from that directory are shown

#### Scenario: Exit submenu with ESC
- **WHEN** the user is in a submenu
- **AND** presses ESC
- **THEN** the menu returns to the parent level

#### Scenario: ESC at root level
- **WHEN** the user is at the root menu level
- **AND** presses ESC
- **THEN** nothing happens (launcher is the home screen)

### Requirement: Manual Hot-Reload

In development mode, the launcher SHALL provide a manual reload mechanism instead of reloading on every ESC.

#### Scenario: Reload key in dev mode
- **WHEN** the run mode is "remote" (development)
- **AND** the user presses 'r' key
- **THEN** the app instance cache is cleared
- **AND** the directories are rescanned
- **AND** the menu is redrawn

#### Scenario: Reload key hidden in flash mode
- **WHEN** the run mode is "flash" (deployed)
- **THEN** the 'r' key has no effect
- **AND** the help text does not show "r=Reload"

### Requirement: Error Handling

The launcher SHALL handle app loading failures gracefully.

#### Scenario: App fails to load
- **WHEN** the user selects an app
- **AND** the app module fails to import (syntax error, missing dependency)
- **THEN** an error message is displayed briefly
- **AND** the user remains in the launcher
