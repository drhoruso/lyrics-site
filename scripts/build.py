#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from string import Template


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
TEMPLATES_DIR = ROOT / "templates"


def load_required_template(path: Path) -> Template:
    if not path.exists():
        raise FileNotFoundError(f"テンプレートが見つかりません: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"テンプレートが空です: {path}")
    return Template(text)


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def render_toc(toc: list[dict]) -> str:
    return "\n        ".join(
        f'<a href="#{esc(item["id"])}">{esc(item["label"])}</a>'
        for item in toc
    )


def first_meta_class(section_index: int) -> str:
    return "meta" if section_index == 0 else "meta mobile-hide"


def render_row(row: dict, *, show_meta: bool, meta_class: str) -> str:
    original_meta = f'<span class="{meta_class}">原文</span>' if show_meta else ""
    translation_meta = f'<span class="{meta_class}">日本語訳</span>' if show_meta else ""

    return (
        '          <div class="row">\n'
        f'            <div class="cell original">{original_meta}<div class="line">{esc(row["original"])}</div></div>\n'
        f'            <div class="cell translation">{translation_meta}<div class="line jp">{esc(row["translation"])}</div></div>\n'
        '          </div>'
    )


def render_rows(section: dict, section_index: int) -> str:
    meta_class = first_meta_class(section_index)
    blocks = [
        render_row(row, show_meta=(i == 0), meta_class=meta_class)
        for i, row in enumerate(section["rows"])
    ]
    return '        <div class="rows">\n' + "\n".join(blocks) + "\n        </div>"


def render_section(section: dict, section_index: int) -> str:
    sec_id = esc(section["id"])
    title = esc(section["title"])
    mood = esc(section["mood"])

    if "instrumental" in section:
        body = f'        <div class="instrumental">{esc(section["instrumental"])}</div>'
    else:
        body = render_rows(section, section_index)

    return (
        f'      <section class="section" id="{sec_id}">\n'
        '        <div class="section-head">\n'
        f'          <h2 class="section-title">{title}</h2>\n'
        f'          <div class="section-mood">{mood}</div>\n'
        '        </div>\n'
        f'{body}\n'
        '      </section>'
    )


def build_song(song_data: dict, song_template: Template) -> tuple[str, str]:
    toc_html = render_toc(song_data["toc"])
    sections_html = "\n\n".join(
        render_section(section, idx)
        for idx, section in enumerate(song_data["sections"])
    )

    html_text = song_template.safe_substitute(
        page_title=esc(song_data["page_title"]),
        kicker=esc(song_data["kicker"]),
        title_ja=esc(song_data["title_ja"]),
        title_en=esc(song_data["title_en"]),
        song_url=esc(song_data["song_url"]),
        subtitle_html=song_data["subtitle_html"],
        note_html=song_data["note_html"],
        song_link_note=esc(song_data.get("song_link_note", "タイトルからも楽曲ページへ移動できます")),
        toc_html=toc_html,
        sections_html=sections_html,
    )
    return song_data["slug"], html_text


def build_index(all_songs: list[dict], index_template: Template) -> str:
    items_html = "\n      ".join(
        (
            f'<li><a class="card" href="./{esc(song["slug"])}/">'
            f'<div class="title">{esc(song["title_ja"])} <span class="en">{esc(song["title_en"])}</span></div>'
            f'<div class="meta">{esc(song["kicker"])}</div>'
            f'</a></li>'
        )
        for song in all_songs
    )
    return index_template.safe_substitute(items_html=items_html)


def collect_song_files(target_slug: str | None) -> list[Path]:
    files = sorted(DATA_DIR.glob("*.json"))
    if target_slug:
        matched = [p for p in files if p.stem == target_slug]
        if not matched:
            raise FileNotFoundError(f"data/{target_slug}.json が見つかりません。")
        return matched
    return [p for p in files if p.stem != "songs"]


def main() -> int:
    target_slug = sys.argv[1] if len(sys.argv) > 1 else None

    song_template = load_required_template(TEMPLATES_DIR / "song.html")
    index_template = load_required_template(TEMPLATES_DIR / "index.html")

    song_files = collect_song_files(target_slug)
    built_songs: list[dict] = []

    for song_file in song_files:
        with song_file.open("r", encoding="utf-8") as f:
            song_data = json.load(f)

        slug, rendered = build_song(song_data, song_template)
        out_dir = ROOT / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(rendered, encoding="utf-8")
        built_songs.append(song_data)
        print(f"built: {slug}/index.html")

    if target_slug is None:
        index_rendered = build_index(built_songs, index_template)
        (ROOT / "index.html").write_text(index_rendered, encoding="utf-8")
        print("built: index.html")

        songs_manifest = [
            {
                "slug": song["slug"],
                "title_ja": song["title_ja"],
                "title_en": song["title_en"],
                "song_url": song["song_url"],
                "kicker": song["kicker"],
            }
            for song in built_songs
        ]
        (DATA_DIR / "songs.json").write_text(
            json.dumps(songs_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print("built: data/songs.json")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
