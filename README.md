# Fix Cursor Default Model

Cursor keeps changing my default model after updates/restarts. I got tired of it, so I made this.

It sets Cursor back to **Auto** and helps keep it there.

Not affiliated with Cursor. Just a local fix.

## Windows

1. Close Cursor
2. Download [`FixCursorDefaultModel.exe`](https://github.com/ameeralichhipa/fix-cursor-default-model/raw/master/bin/FixCursorDefaultModel.exe)
3. Run it
4. In Cursor go to **Settings → Agents → Conversation**
5. Set **Default Model** to **Last Used**
6. Reload window (`Ctrl+Shift+P` → Developer: Reload Window)
7. Open a new chat and check it's on Auto

If Windows blocks it: More info → Run anyway.

## Mac

```bash
git clone https://github.com/ameeralichhipa/fix-cursor-default-model.git
cd fix-cursor-default-model
chmod +x fix-cursor-default-model.command
xattr -dr com.apple.quarantine .
```

Double-click `fix-cursor-default-model.command`, then do the same **Last Used** + reload steps as above.

## Or just run the Python script

```bash
python fix_cursor_default_model.py
```

Works on Windows / Mac / Linux if Python is installed.

## Notes

- It only changes local Cursor files on your machine
- It makes a backup of `state.vscdb` before writing
- If Cursor flips the model again after an update, just run it again

## License

MIT
