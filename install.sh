#!/usr/bin/env bash
set -e

GAME_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$GAME_DIR/.venv"

echo "==> Space Game Installer"
echo "    Spielverzeichnis: $GAME_DIR"

# venv anlegen falls nicht vorhanden
if [ ! -d "$VENV" ]; then
    echo "==> Erstelle virtuelle Umgebung..."
    python3 -m venv "$VENV"
else
    echo "==> Virtuelle Umgebung bereits vorhanden."
fi

# pygame installieren
echo "==> Installiere/prüfe pygame..."
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet pygame

# alias in ~/.bashrc eintragen (idempotent)
ALIAS_LINE="alias spacegame='$VENV/bin/python $GAME_DIR/main.py'"
if grep -qxF "$ALIAS_LINE" ~/.bashrc 2>/dev/null; then
    echo "==> Alias 'spacegame' bereits in ~/.bashrc vorhanden."
else
    echo "$ALIAS_LINE" >> ~/.bashrc
    echo "==> Alias 'spacegame' zu ~/.bashrc hinzugefügt."
fi

echo ""
echo "Fertig! Starte das Spiel mit:"
echo "    spacegame"
echo ""
echo "Falls der Alias noch nicht funktioniert:"
echo "    source ~/.bashrc"
echo "    spacegame"
