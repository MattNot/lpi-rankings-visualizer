# LPI Rankings Visualizer

Generatore di classifiche per la Lega Pauper Cosenza a partire dai dati pubblicati dall'API del sito ufficiale.

Il progetto recupera la classifica di una stagione, la rende in HTML con uno stile dedicato e, opzionalmente, esporta anche una versione PNG.

## Funzionalità

- recupera la classifica di una stagione tramite API
- genera una pagina HTML pronta per stampa o condivisione
- supporta una configurazione personalizzata del tema e del layout
- include logo personalizzato o fallback testuale
- esporta immagine PNG con Playwright

## Requisiti

- Python 3.10+
- dipendenze di Python elencate in `requirements.txt`

Installa le dipendenze:

```bash
python -m pip install -r requirements.txt
```

Se vuoi generare anche il PNG, installa il browser Chromium di Playwright:

```bash
python -m playwright install chromium
```

## Esecuzione

Esempio base:

```bash
python ranking_visualizer.py 221
```

Questo crea un file `ranking_221.html` nella cartella del progetto.

### Opzioni disponibili

```bash
python ranking_visualizer.py 221 --output ranking_finale.html
python ranking_visualizer.py 221 --config config.example.json
python ranking_visualizer.py 221 --png
python ranking_visualizer.py 221 --png --scale 3
```

### Parametri principali

- `season_id`: ID della stagione da visualizzare (default: `221`)
- `-o, --output`: percorso del file HTML di output
- `--config`: percorso del file JSON di configurazione
- `--png`: genera anche il file PNG
- `--scale`: risoluzione del PNG (`3` è il default e produce una qualità elevata)

## Configurazione

Il file `config.example.json` contiene i valori predefiniti:

```json
{
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
  "show_decks": true,
  "max_rows": 16
}
```

### Campi personalizzabili

- `title`: titolo mostrato nella pagina
- `accent`: colore principale
- `background`, `panel`, `text`, `muted`, `divider`: palette del tema
- `font_family`, `display_font`: font usati nel layout
- `font_url`: URL del CSS dei font esterni
- `logo_path`: percorso del logo da utilizzare
- `show_decks`: mostra il mazzo giocato di ciascun player
- `max_rows`: numero massimo di righe visualizzate

## Output

Il comando genera in genere:

- `ranking_{season_id}.html`
- `ranking_{season_id}.png` se usata l'opzione `--png`

## Struttura del progetto

- `ranking_visualizer.py`: script principale
- `config.example.json`: configurazione di esempio
- `assets/`: risorse grafiche, inclusi logo e asset statici

## Note

Il tool usa l'endpoint API pubblico del sito e tenta di recuperare anche il nome della stagione. Se l'API non risponde come previsto, il programma solleva un errore esplicito con un messaggio chiaro.
