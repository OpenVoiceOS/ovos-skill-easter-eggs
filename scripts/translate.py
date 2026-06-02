import os
from os.path import dirname, join, exists
from ovos_utils.bracket_expansion import expand_options
from googletranslate_neon_plugin import GoogleTranslator

tx = GoogleTranslator()

src_lang = "en-US"
target_langs = ["es-ES", "de-DE", "fr-FR", "it-IT", "pt-PT"]

exts = [".voc", ".dialog", ".intent", ".entity"]
res_folder = join(dirname(dirname(__file__)), "locale")
target_langs = list(set(target_langs + os.listdir(res_folder)))

src_files = {}
for root, dirs, files in os.walk(res_folder):
    if src_lang not in root:
        continue
    for f in files:
        if any(f.endswith(e) for e in exts):
            src_files[f] = join(root, f)

for lang in target_langs:
    os.makedirs(join(res_folder, lang), exist_ok=True)

    for name, src in src_files.items():
        dst = join(res_folder, lang, name)
        if exists(dst):
            continue

        tx_lines = []
        with open(src) as f:
            lines = [line for line in f.read().split("\n") if line and not line.startswith("#")]

        for line in lines:
            expanded = expand_options(line)
            for expanded_line in expanded:
                try:
                    translated = tx.translate(expanded_line, target=lang, source=src_lang)
                    tx_lines.append(translated)
                except Exception:
                    continue

        with open(dst, "w") as f:
            f.write(f"# auto translated from {src_lang} to {lang}\n")
            for translated in set(tx_lines):
                f.write(translated + "\n")
