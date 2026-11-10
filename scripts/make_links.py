#!/usr/bin/env python3
"""Print each person's two share links (REALITY + Hysteria2) from a local creds file.

    python3 make_links.py creds.json            # print links
    python3 make_links.py creds.json --qr out/  # also write QR PNGs (needs `qrencode`)

Keep creds.json out of git and out of chat apps that scan content.
Hand the QR codes over in person, or through an end-to-end encrypted channel.
"""
import json, os, subprocess, sys, shutil
from urllib.parse import quote


def links(g, name, u):
    host = g["entry_host"]
    r = ("vless://%s@%s:443?encryption=none&flow=xtls-rprx-vision&security=reality"
         "&sni=%s&fp=chrome&pbk=%s&sid=%s&type=tcp#%s"
         % (u["uuid"], host, g["reality"]["sni"], g["reality"]["public_key"],
            g["reality"]["short_id"], quote("home-steady-" + name)))
    h = ("hysteria2://%s@%s:%d?obfs=salamander&obfs-password=%s&sni=%s&insecure=1#%s"
         % (quote(u["hy2"], safe=""), host, g["hy2"]["port"],
            quote(g["hy2"]["obfs_password"], safe=""), g["reality"]["sni"],
            quote("home-fast-" + name)))
    return r, h


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    g = json.load(open(sys.argv[1]))
    qr_dir = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--qr" else None
    if qr_dir:
        if not shutil.which("qrencode"):
            sys.exit("qrencode not found (apt install qrencode / brew install qrencode)")
        os.makedirs(qr_dir, mode=0o700, exist_ok=True)
    for name, u in g["users"].items():
        r, h = links(g, name, u)
        print("== %s\n%s\n%s\n" % (name, r, h))
        if qr_dir:
            for tag, link in (("steady", r), ("fast", h)):
                out = os.path.join(qr_dir, "%s-%s.png" % (name, tag))
                subprocess.run(["qrencode", "-s", "8", "-o", out, link], check=True)
                os.chmod(out, 0o600)


if __name__ == "__main__":
    main()
