# Cardputer ADV Troubleshooting

## When mpremote Can't Connect (Launcher Blocking)

If the built-in launcher or your code is blocking mpremote from connecting:

### Step 1: Use screen instead of mpremote

```bash
screen /dev/tty.usbmodem2101 115200
```

### Step 2: Interrupt the running program

Press **Ctrl+C** several times until you see:
```
KeyboardInterrupt:
raw REPL; CTRL-B to exit
>
```

### Step 3: Enter normal REPL

Press **Ctrl+B** to exit raw REPL. You should see:
```
MicroPython v1.25.0 on ...; M5STACK Cardputer with ESP32-S3-FN8
Type "help()" for more information.
>>>
```

### Step 4: Fix the boot option

```python
import esp32; nvs=esp32.NVS("uiflow"); nvs.set_u8("boot_option",0); nvs.commit()
```

### Step 5: Exit screen

Press **Ctrl+A**, then **K**, then **Y** to confirm.

### Step 6: Reconnect with mpremote

```bash
mpremote connect /dev/tty.usbmodem2101 mount ~/projects/src/github.com/TheRealHaoLiu/cardputer + repl
```

---

## REPL Modes

| Mode | How to Enter | Prompt | Use |
|------|--------------|--------|-----|
| Normal REPL | Ctrl+B from raw REPL | `>>>` | Interactive Python |
| Raw REPL | Ctrl+A from normal REPL | `>` | Machine-to-machine (mpremote uses this) |

---

## Boot Options (NVS)

```python
import esp32
nvs = esp32.NVS("uiflow")

# Read current value
nvs.get_u8("boot_option")

# Set value
nvs.set_u8("boot_option", VALUE)
nvs.commit()
```

| Value | Behavior |
|-------|----------|
| 0 | Run /flash/main.py directly (blank screen if no main.py) |
| 1 | Show built-in launcher menu |
| 2 | Network setup only |

**For development with mpremote, use `boot_option = 0`**

---

## Quick Reference

| Action | Keys |
|--------|------|
| Interrupt running code | Ctrl+C |
| Enter raw REPL | Ctrl+A |
| Exit raw REPL to normal | Ctrl+B |
| Soft reset | Ctrl+D |
| Exit screen | Ctrl+A, K, Y |
| Exit mpremote repl | Ctrl+] or Ctrl+X |

---

## Initialize NVS for Built-in Launcher (DON'T DO IT)

If launcher fails with `ESP_ERR_NVS_NOT_FOUND`, run:

```python
exec(open('/remote/init_nvs.py').read())
```

Or manually:
```python
import esp32
nvs = esp32.NVS("uiflow")
nvs.set_str("net_mode", "WIFI")
nvs.set_str("ssid0", "")
nvs.set_str("pswd0", "")
nvs.set_str("protocol", "DHCP")
nvs.set_str("ip_addr", "")
nvs.set_str("netmask", "")
nvs.set_str("gateway", "")
nvs.set_str("dns", "")
nvs.set_str("server", "uiflow2.m5stack.com")
nvs.set_u8("boot_option", 1)
nvs.commit()
```
