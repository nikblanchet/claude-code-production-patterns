# Attention Chime for Claude Code

## What It Is

An audio notification that plays when Claude Code is waiting for user input. This helps capture your attention when managing multiple Claude Code instances, so you know when an instance needs your response.

## How It Works

The chime uses Claude Code's **Notification hook** system:

1. When Claude Code waits for user input (after completing tool execution or needing a decision), it triggers a notification event
2. The Notification hook executes the configured command
3. The command plays a system sound using macOS's built-in `afplay` audio player
4. You hear a gentle chime, alerting you that Claude needs attention

## Current Configuration

**Location:** `~/.claude/settings.json` (global configuration, applies to all projects)

**Configuration:**
```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Glass.aiff"
          }
        ]
      }
    ]
  }
}
```

**Key elements:**
- **Hook type:** `Notification` - fires when Claude needs user attention
- **Matcher:** `""` (empty) - applies to all notification events
- **Command:** `afplay /System/Library/Sounds/Glass.aiff` - plays the "Glass" system sound
- **Scope:** Global (affects all Claude Code projects)

## How to Recreate This Setup

### Step 1: Locate Your Claude Code Settings File

Open or create: `~/.claude/settings.json`

```bash
# Check if file exists
ls -la ~/.claude/settings.json

# If directory doesn't exist, create it
mkdir -p ~/.claude

# Create or edit the settings file
nano ~/.claude/settings.json  # or use your preferred editor
```

### Step 2: Add the Notification Hook

If the file is empty or new, add:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Glass.aiff"
          }
        ]
      }
    ]
  }
}
```

If the file already has content, merge the `Notification` hook into your existing `hooks` configuration.

### Step 3: Verify the Sound Works

Test the command directly:

```bash
afplay /System/Library/Sounds/Glass.aiff
```

You should hear a gentle glass chime sound.

### Step 4: Restart Claude Code

The configuration takes effect when Claude Code starts, so:
1. Exit all Claude Code instances
2. Restart Claude Code
3. Run a command that requires user input - you should hear the chime

## Customization Options

### Alternative System Sounds

macOS includes many built-in sounds you can use. Browse them:

```bash
ls /System/Library/Sounds/
```

**Popular options:**
- `Glass.aiff` - Gentle glass chime (current setting)
- `Hero.aiff` - Heroic fanfare
- `Ping.aiff` - Simple ping
- `Pop.aiff` - Subtle pop
- `Tink.aiff` - Light metallic tink
- `Submarine.aiff` - Sonar ping
- `Blow.aiff` - Wind blow
- `Bottle.aiff` - Bottle pop

**To change the sound**, replace the path in your configuration:

```json
"command": "afplay /System/Library/Sounds/Ping.aiff"
```

### Custom Sound Files

You can use any `.aiff`, `.wav`, or `.mp3` file:

```json
"command": "afplay /path/to/your/custom-sound.aiff"
```

Example:
```json
"command": "afplay ~/Documents/Sounds/attention-chime.wav"
```

### Volume Control

`afplay` doesn't have built-in volume control, but you can use `osascript` to set system volume temporarily:

```bash
# Play at lower volume (example - not recommended as it changes system volume)
osascript -e "set volume output volume 30" && afplay /System/Library/Sounds/Glass.aiff && osascript -e "set volume output volume 50"
```

Note: This changes system volume, which may affect other applications.

## Project-Specific Override

To use a different sound for a specific project, create a project-level settings file:

**Location:** `/path/to/your/project/.claude/settings.local.json`

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Hero.aiff"
          }
        ]
      }
    ]
  }
}
```

Project-level settings override global settings for that specific project.

## Troubleshooting

### No Sound Plays

**Check 1: Verify afplay works**
```bash
afplay /System/Library/Sounds/Glass.aiff
```
If no sound, check system volume and audio output device.

**Check 2: Verify settings file syntax**
```bash
# Check for JSON syntax errors
cat ~/.claude/settings.json | python3 -m json.tool
```
Should output formatted JSON without errors.

**Check 3: Check file permissions**
```bash
ls -la ~/.claude/settings.json
```
Should be readable by your user.

**Check 4: Restart Claude Code**
Settings are loaded at startup. Fully quit and restart.

### Sound Plays Multiple Times

The hook may be triggering for multiple notification types. To restrict it, use a specific matcher:

```json
{
  "matcher": "waiting_for_input",  // Example - adjust to actual event name
  "hooks": [...]
}
```

(Note: You may need to check Claude Code documentation for specific matcher values)

### Sound File Not Found

If using a custom sound file, verify the path exists:

```bash
ls -la /path/to/your/sound.aiff
```

Use absolute paths, not relative paths (starting with `/` or `~/`).

## Platform Compatibility

**macOS:** Fully supported (uses `afplay`)

**Linux:** Replace `afplay` with `aplay`, `paplay`, or another audio player:
```json
"command": "aplay /usr/share/sounds/alsa/Front_Center.wav"
```

**Windows:** Replace with PowerShell or `powershell.exe` command:
```json
"command": "powershell -c (New-Object Media.SoundPlayer 'C:\\Windows\\Media\\Windows Notify.wav').PlaySync()"
```

## Technical Details

**Hook Execution:**
- Runs asynchronously (doesn't block Claude Code)
- No timeout specified (executes quickly for simple commands)
- Runs in a shell subprocess with access to system commands

**Security:**
- Hooks run with your user permissions
- No sandboxing - can execute any command you can run in terminal
- Keep hooks simple and avoid untrusted commands

**Performance:**
- `afplay` is lightweight and executes in milliseconds
- System sounds are small files (< 100KB)
- Minimal impact on Claude Code responsiveness

## See Also

- Claude Code hooks documentation: Check official docs for all available hook types
- SessionStart hook: Runs commands when Claude Code session starts (also configured in this project)
- Other hook types: Error hooks, completion hooks, etc.

## Example: Multiple Notification Sounds

You can configure different sounds for different events using matchers:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "waiting_for_input",
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Glass.aiff"
          }
        ]
      },
      {
        "matcher": "error",
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Basso.aiff"
          }
        ]
      }
    ]
  }
}
```

This would play different sounds for different notification types (if matchers are supported - check Claude Code documentation).
