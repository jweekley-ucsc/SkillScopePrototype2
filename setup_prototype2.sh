#!/bin/bash

# Adjust these paths if your source files are located elsewhere
SOURCE_DIR="."
TARGET_DIR=~/Documents/SkillScope/Prototype2

echo "🔧 Creating directory structure at $TARGET_DIR ..."
mkdir -p "$TARGET_DIR/templates"
mkdir -p "$TARGET_DIR/static/scripts"

echo "📁 Copying HTML templates ..."
cp "$SOURCE_DIR"/login.html "$TARGET_DIR/templates/"
cp "$SOURCE_DIR"/interview.html "$TARGET_DIR/templates/"
cp "$SOURCE_DIR"/interviewer.html "$TARGET_DIR/templates/"
cp "$SOURCE_DIR"/admin.html "$TARGET_DIR/templates/"

echo "📁 Copying JavaScript files ..."
cp "$SOURCE_DIR"/interview.js "$TARGET_DIR/static/scripts/"
cp "$SOURCE_DIR"/interviewer.js "$TARGET_DIR/static/scripts/"
cp "$SOURCE_DIR"/admin.js "$TARGET_DIR/static/scripts/"

echo "📁 Copying Python and config files ..."
cp "$SOURCE_DIR"/server.py "$TARGET_DIR/"
cp "$SOURCE_DIR"/requirements.txt "$TARGET_DIR/"

echo "✅ Prototype2 setup complete."
