import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
def load_config():
    return json.loads((ROOT / "config.json").read_text())
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
