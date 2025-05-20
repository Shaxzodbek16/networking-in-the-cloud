import polib
from deep_translator import GoogleTranslator
import time

# 1. Load your .po
po_path = "locale/uz/LC_MESSAGES/django.po"
po = polib.pofile(po_path)

# 2. Loop and translate
for entry in po:
    # Skip header and already‐translated
    if not entry.msgid or entry.msgstr.strip():
        continue

    # Translate
    entry.msgstr = GoogleTranslator(source='auto', target='uz') \
                       .translate(text=entry.msgid)
    print(f"→ {entry.msgid[:30]}… → {entry.msgstr[:30]}…")
    time.sleep(0.1)   # be gentle on the API

# 3. Save
po.save(po_path)
print("✅ Translations complete. Now run: django-admin compilemessages")