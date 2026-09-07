from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

API_BASE = "https://www.elmariachistudios.it/ws"
DEFAULT_CONFIG = {
	"title": "Season Ranking",
	"accent": "#b33b34",
	"background": "#f7f8f8",
	"panel": "#ffffff",
	"text": "#263b52",
	"muted": "#657587",
	"divider": "#dbe1e5",
	"font_family": "Montserrat",
	"display_font": "Oswald",
	"font_url": "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Oswald:wght@500;600;700&display=swap",
	"logo_path": "assets/logo-lpc-color.png",
	"show_decks": True,
	"max_rows": 16,
}


@dataclass
class Player:
	position: int
	name: str
	base_points: float
	bonus_points: float
	stages_played: int
	average: float
	deck: str


def fetch_json(url: str) -> dict[str, Any]:
	response = requests.get(url, timeout=30)
	response.raise_for_status()
	result = response.json()
	if not isinstance(result, dict):
		raise ValueError(f"Risposta inattesa da {url}")
	return result


def as_number(value: Any) -> float:
	try:
		return float(value)
	except (TypeError, ValueError):
		return 0


def fetch_ranking(season_id: int) -> tuple[list[Player], str]:
	ranking = fetch_json(f"{API_BASE}/seasons/{season_id}/ranking")
	raw_players = ranking.get("payLoad")
	if not isinstance(raw_players, list) or not raw_players:
		raise ValueError(ranking.get("errorMsg") or "Nessun partecipante trovato")
	players = []
	for position, raw in enumerate(raw_players, 1):
		decks = raw.get("decksPlayed") or []
		players.append(Player(
			position=position,
			name=str(raw.get("name") or "Giocatore").strip(),
			base_points=as_number(raw.get("totalPoints")),
			bonus_points=as_number(raw.get("bonusPoints")),
			stages_played=int(as_number(raw.get("stagesPlayed"))),
			average=as_number(raw.get("pointsPerStage")),
			deck=str(decks[0]).title().strip() if decks else "",
		))
	season_name = f"Season {season_id}"
	try:
		details = fetch_json(f"{API_BASE}/seasons/{season_id}").get("payLoad") or {}
		season_name = str(details.get("name") or season_name)
	except requests.RequestException:
		pass
	return players, season_name


def load_config(path: str | None) -> dict[str, Any]:
	config = DEFAULT_CONFIG.copy()
	config["_base_dir"] = str(Path(__file__).resolve().parent)
	if path:
		with open(path, encoding="utf-8") as file:
			config.update(json.load(file))
		config["_base_dir"] = str(Path(path).resolve().parent)
	return config


def logo_markup(config: dict[str, Any]) -> str:
	path = Path(str(config.get("logo_path", "")))
	if not path.is_absolute():
		path = Path(str(config.get("_base_dir") or Path.cwd())) / path
	if path.is_file():
		mime = mimetypes.guess_type(path.name)[0] or "image/png"
		encoded = base64.b64encode(path.read_bytes()).decode("ascii")
		return f'<img class="logo" src="data:{mime};base64,{encoded}" alt="Lega Pauper Cosenza">'
	return '<div class="wordmark">LEGA PAUPER <strong>COSENZA</strong></div>'


def render_html(season_id: int, season_name: str, players: list[Player], config: dict[str, Any]) -> str:
	colors = {key: str(config.get(key, DEFAULT_CONFIG[key])) for key in ("accent", "background", "panel", "text", "muted", "divider")}
	font_url = html.escape(str(config.get("font_url", "")), quote=True)
	font_import = f'@import url("{font_url}");' if font_url.startswith("https://") else ""
	title = html.escape(str(config.get("title", "Season Ranking")))
	rows = players[:max(1, int(config.get("max_rows", len(players))))]
	show_decks = bool(config.get("show_decks", True))
	rendered_rows = []
	for player in rows:
		total = player.base_points + player.bonus_points
		deck = html.escape(player.deck) if show_decks else ""
		note = f"{player.base_points:g} base + {player.bonus_points:g} bonus - media {player.average:g}"
		rendered_rows.append(f'''<div class="ranking-row rank-{min(player.position, 4)}">
<div class="position p-{min(player.position, 4)}">{player.position}</div>
<div class="player"><strong>{html.escape(player.name)}</strong><span>{deck}</span></div>
<div class="stat points"><strong>{total:g}</strong><span>PT TOTALI</span><small>{note}</small></div>
<div class="stat"><strong>{player.stages_played}</strong><span>TAPPE</span></div>
</div>''')
	css = f'''{font_import}
:root {{ --accent:{colors["accent"]}; --background:{colors["background"]}; --panel:{colors["panel"]}; --text:{colors["text"]}; --muted:{colors["muted"]}; --divider:{colors["divider"]}; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:#d6dce1; color:var(--text); font-family:"{config.get("font_family", "Montserrat")}", sans-serif; }}
.canvas {{ position:relative; overflow:hidden; width:min(100%,1080px); min-height:1350px; margin:auto; padding:48px 64px 38px; background:linear-gradient(145deg,#fff, #ebf0f3); }}
.canvas::before {{ position:absolute; inset:18px; border:1px solid rgba(38,59,82,.18); content:""; pointer-events:none; }} .canvas::after {{ position:absolute; top:0; left:0; width:100%; height:14px; background:var(--accent); content:""; }}
header {{ display:flex; justify-content:center; border-bottom:4px solid var(--text); padding:20px 14px 22px; margin-bottom:24px; text-align:center; }}
.header-copy {{ min-width:0; }} .logo {{ display:block; width:auto; max-width:340px; max-height:140px; object-fit:contain; margin:0 auto 13px; }} .wordmark {{ margin:0 0 15px; font-family:"{config.get("display_font", "Oswald")}", sans-serif; font-size:28px; font-weight:700; }} .wordmark strong {{ color:var(--accent); }}
h1 {{ color:var(--text); font-family:"{config.get("display_font", "Oswald")}", sans-serif; font-size:clamp(38px,5vw,60px); letter-spacing:.02em; line-height:1; margin:0; text-transform:uppercase; }} .season {{ margin:9px 0 0; color:var(--muted); font-size:18px; font-weight:600; }}
.ranking {{ position:relative; z-index:1; background:var(--panel); border:2px solid var(--text); box-shadow:8px 8px 0 rgba(38,59,82,.14); }} .table-head,.ranking-row {{ display:grid; grid-template-columns:58px minmax(0,1fr) 166px 70px; align-items:center; column-gap:14px; }}
.table-head {{ min-height:42px; padding:0 19px; background:var(--text); color:var(--background); font-size:10px; letter-spacing:.16em; font-weight:800; }} .table-head span:nth-child(n+3),.stat {{ text-align:center; }}
.ranking-row {{ min-height:68px; padding:9px 19px; background:var(--panel); border-top:1px solid var(--divider); }} .ranking-row:nth-child(even) {{ background:#f1f4f5; }} .position {{ width:38px; height:38px; display:grid; place-items:center; border:2px solid var(--muted); border-radius:50%; color:var(--muted); font-size:16px; font-weight:800; }}
.rank-1 {{ background:#fff1bd; }} .rank-2 {{ background:#e8edf0; }} .rank-3 {{ background:#f1d8cb; }} .p-1 {{ border-color:#a87908; background:#d3a52f; color:#fff; }} .p-2 {{ border-color:#7e8d98; background:#aebbc3; color:#fff; }} .p-3 {{ border-color:#9d5c43; background:#c47d5c; color:#fff; }} .player {{ min-width:0; text-align:left; }} .player strong {{ display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:17px; }} .player span {{ display:block; margin-top:4px; color:var(--muted); font-size:10px; text-transform:uppercase; letter-spacing:.08em; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.stat strong {{ display:block; font-size:19px; }} .stat span {{ display:block; margin-top:3px; color:var(--muted); font-size:9px; letter-spacing:.1em; font-weight:800; }} .stat small {{ display:block; margin-top:3px; color:var(--muted); font-size:9px; white-space:nowrap; }} .points strong {{ color:var(--accent); font-size:24px; }} footer {{ display:flex; justify-content:space-between; margin:18px 14px 0; color:var(--muted); font-size:11px; }} footer strong {{ color:var(--text); }}
@media (max-width:720px) {{ .canvas {{ min-height:100vh; padding:34px 18px; }} .canvas::before {{ inset:10px; }} .logo {{ max-width:245px; max-height:110px; }} h1 {{ font-size:38px; }} .season {{ font-size:16px; }} .table-head,.ranking-row {{ grid-template-columns:40px minmax(0,1fr) 104px; column-gap:10px; padding-left:12px; padding-right:12px; }} .table-head .hide-mobile,.ranking-row .stat:not(.points) {{ display:none; }} .ranking-row {{ min-height:67px; }} .player strong {{ font-size:15px; }} .points strong {{ font-size:20px; }} .points small {{ font-size:8px; }} footer {{ gap:12px; flex-wrap:wrap; }} }}
@media print {{ .canvas {{ width:1080px; }} }}'''
	return f'''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} - {html.escape(season_name)}</title><style>{css}</style></head><body><main class="canvas"><header><div class="header-copy">{logo_markup(config)}<h1>{title}</h1><p class="season">{html.escape(season_name)}</p></div></header><section class="ranking"><div class="table-head"><span>#</span><span>PLAYER</span><span>POINTS</span><span>STAGES</span></div>{''.join(rendered_rows)}</section><footer><span><strong>{len(players)}</strong> partecipanti</span><span>Updated automatically</span></footer></main></body></html>'''


def main() -> None:
	parser = argparse.ArgumentParser(description="Genera la classifica LPI in HTML e PNG.")
	parser.add_argument("season_id", nargs="?", type=int, default=221)
	parser.add_argument("-o", "--output", default=None)
	parser.add_argument("--config")
	parser.add_argument("--png", action="store_true")
	parser.add_argument("--scale", type=float, default=3, help="Densita PNG: 3 = alta qualita (default)")
	args = parser.parse_args()
	config = load_config(args.config)
	players, season_name = fetch_ranking(args.season_id)
	output = Path(args.output or f"ranking_{args.season_id}.html")
	output.write_text(render_html(args.season_id, season_name, players, config), encoding="utf-8")
	print(f"Creato: {output.resolve()} ({len(players)} partecipanti)")
	if args.png:
		try:
			from playwright.sync_api import sync_playwright
		except ImportError as error:
			raise SystemExit("Per --png installa: python -m pip install playwright; python -m playwright install chromium") from error
		png_path = output.with_suffix(".png")
		with sync_playwright() as playwright:
			browser = playwright.chromium.launch()
			page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=args.scale)
			page.goto(output.resolve().as_uri(), wait_until="networkidle")
			page.screenshot(path=str(png_path), full_page=True)
			browser.close()
		print(f"Creato: {png_path.resolve()}")


if __name__ == "__main__":
	main()
