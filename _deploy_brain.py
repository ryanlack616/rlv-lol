"""Update brain files on rlv.lol (Porkbun static hosting) and remove contact section."""
from __future__ import annotations

import ftplib
import os
import re
import ssl
import sys
from pathlib import Path

HERE = Path(__file__).parent
FTP_HOST = "pixie-ss1-ftp.porkbun.com"
FTP_USER = "rlv.lol"
FTP_PASS = os.environ.get("RLV_FTP_PASS", "")

PERSIST = Path("/home/ryan/rje/howell-persist")

# Files to upload: (source_path, remote_path)
FILES = [
    # Identity
    (PERSIST / "SOUL.md", "brain/identity/SOUL.md"),
    (PERSIST / "CONTEXT.md", "brain/identity/CONTEXT.md"),
    (PERSIST / "PROJECTS.md", "brain/identity/PROJECTS.md"),
    (PERSIST / "QUESTIONS.md", "brain/identity/QUESTIONS.md"),
    # Memory
    (PERSIST / "memory/PINNED.md", "brain/memory/PINNED.md"),
    (PERSIST / "memory/RECENT.md", "brain/memory/RECENT.md"),
    (PERSIST / "memory/SUMMARY.md", "brain/memory/SUMMARY.md"),
    # Procedures
    (PERSIST / "procedures/README.md", "brain/procedures/README.md"),
    (PERSIST / "procedures/backup.md", "brain/procedures/backup.md"),
    (PERSIST / "procedures/comfyui-generate.md", "brain/procedures/comfyui-generate.md"),
    (PERSIST / "procedures/howell-daemon.md", "brain/procedures/howell-daemon.md"),
    (PERSIST / "procedures/memory-system.md", "brain/procedures/memory-system.md"),
    (PERSIST / "procedures/moltbook-api.md", "brain/procedures/moltbook-api.md"),
    (PERSIST / "procedures/netlify-deploy.md", "brain/procedures/netlify-deploy.md"),
]


def main() -> int:
    if not FTP_PASS:
        print("ERROR: set RLV_FTP_PASS env var first.")
        return 1

    # 1. Upload brain files
    print(f"Uploading {len(FILES)} brain files...")
    ctx = ssl.create_default_context()
    with ftplib.FTP_TLS(FTP_HOST, context=ctx) as ftp:
        ftp.login(FTP_USER, FTP_PASS)
        ftp.prot_p()
        for local_path, remote_rel in FILES:
            if not local_path.exists():
                print(f"  SKIP (not found): {local_path.name}")
                continue
            parts = remote_rel.split("/")
            for i in range(1, len(parts)):
                d = "/".join(parts[:i])
                try:
                    ftp.mkd(d)
                except ftplib.error_perm:
                    pass
            with open(local_path, "rb") as fh:
                size = local_path.stat().st_size
                print(f"  {remote_rel}  ({size:,} B)")
                ftp.storbinary(f"STOR {remote_rel}", fh)

    # 2. Remove contact section from index.html
    print("\nUpdating index.html (removing contact section)...")
    index_path = HERE / "index.html"
    content = index_path.read_text("utf-8")
    new_content = re.sub(
        r'<section class="contact">.*?</section>\n',
        "",
        content,
        flags=re.DOTALL,
    )
    index_path.write_text(new_content, "utf-8")
    print(f"  Removed contact section ({len(content) - len(new_content)} chars)")

    # Upload updated index.html
    with ftplib.FTP_TLS(FTP_HOST, context=ctx) as ftp:
        ftp.login(FTP_USER, FTP_PASS)
        ftp.prot_p()
        with open(index_path, "rb") as fh:
            size = index_path.stat().st_size
            print(f"  Uploading index.html ({size:,} B)")
            ftp.storbinary("STOR index.html", fh)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
