# fab_sound_clap_meter

Applausometro generico: piu' ingressi audio -> dB -> punteggio 1.0-10.0.

## Avvio
    pip install -r requirements.txt
    cd fab_sound_clap_meter
    python main.py

Test: `python -m pytest tests`

## Architettura (dipendenze verso l'interno)
- `domain/`          logica pura, senza Qt: mixer pesato, mapper della scala, calibrazione, smoothing, filtro spike, min/max
- `applause_analyzer/` algoritmi che producono `applause_score` (pura logica, registro di algoritmi)
- `manche/`          la gara: manche, turni, voti, punteggi, tabellone, spareggio, modelli (pura logica, senza Qt)
- `audio/`           QtMultimedia + numpy: apertura ingressi e misura dei dBFS
- `application/`     `ClapMeterEngine` (facciata per QML) e `ChannelController` (un ingresso)
- `infrastructure/`  salvataggio JSON impostazioni, scoperta degli stili
- `ui/qml/`          finestra operatore e finestra pubblico (`styles/` grafiche, `palettes/` colori)
- `assets/`          `icon.png` (icona dell'app, vedi `assets/README.md`)

## Formula multi-ingresso
P = sum(w_i * 10^(dB_i/10)) / sum(w_i);  dB = 10*log10(P)   (pesi 1-10 per ingresso)

## Nuovo stile per il pubblico
Copia `ui/qml/styles/BarStyle.qml` in `<Nome>Style.qml` e ridisegna: appare da solo nel selettore.
Lo stile riceve `meter` (score, scoreText, combinedDb, floorDb, peakDb, channels[...]).

## Valori disponibili per gli stili pubblico (`meter.*`)
`actual_score` (live, alias `score`), `max_score`, `min_score`, `scale_max`, `scale_min`,
`applause_score` (live), `applause_final_score`, `applause_running`.

## Aggiungere un algoritmo applause
1. Crea una classe che estende `ApplauseAlgorithm` (nome, `definitions` dei parametri, `reset`, `feed`).
2. Registrala in `applause_analyzer/default_registry.py`.
L'interfaccia dei parametri nella sezione "Applause Algorithm" si costruisce da sola.

## Backend per la scheda Manche
`startApplauseAnalyzer()` e `stopApplauseAnalyzer()` (slot di `ClapMeterEngine`). Di default l'analizzatore e' fermo.

## Spike filter
`domain/spike_filter.py`: decide guardando in avanti (ritardo = durata massima + 200 ms di calma).
Un picco sopra `base + soglia` che dura meno della durata massima ed e' seguito da calma viene sostituito con la base;
un gruppo lungo o ripetuto (applauso) passa intatto. Parametri in `Calibrazione`: soglia dB e durata massima ms.

## Palette colori
Ogni palette e' un file `ui/qml/palettes/<Nome>Palette.qml` che eredita da `ScorePaletteBase.qml` e imposta i colori
(sfondo, parti vuote, testo, colore Applause, colori della scala 1-10). Appare da sola nel menu "Color Palette"
(`PorporaStylePalette.qml` -> "Porpora Style"). Gli stili leggono tutto da `colors` e non hanno colori scritti nel codice,
quindi ogni palette funziona con ogni stile. Palette incluse: `Default` (colori originali) e `Porpora Style`.
La palette colora anche il **pannello operatore**: `ui/qml/Theme.qml` (singleton) tiene la palette attiva e
`OperatorWindow.qml` la carica; `SectionCard`, `LiveDbBar` e i controlli Material leggono da `Theme.colors`.
Ruoli per l'operatore (facoltativi, se mancano si ricavano dai colori base): `windowColor`, `headerColor`, `surface`,
`border`, `controlAccent`, `meterTrack`, `meterFill`, `markerLow`, `markerHigh`.
Nei file QML dell'operatore non vanno scritti colori fissi: usa sempre `Theme.colors.<ruolo>`.

## Icona dell'app
Metti `assets/icon.png` (PNG quadrato 512x512, sfondo trasparente). Viene usata nella barra del titolo e nella barra
delle applicazioni. Se manca, l'app parte lo stesso. Su Windows l'app si registra con un proprio identificativo
(`infrastructure/app_icon.py`) cosi' la barra mostra la tua icona e non quella di Python.

## Scheda Manche
**Regole** (`manche/`, senza Qt, tutto testato): `race.py` e' l'unico punto che modifica la gara (configurazione annullabile,
blocco durante la misura e dopo la proclamazione, sessioni, sostituzioni, misure straordinarie, spareggio, modelli);
`sequence.py` (ordine dei turni), `scoring.py` (media/somma/massimo/ultimo, totali, parita' ai centesimi),
`presenter.py` (dati e testi per la grafica).
**Collegamento** (`application/manche_controller.py`): traduce i comandi della grafica in operazioni sulla gara e collega
l'analizzatore. Il voto di un turno e' `applause_final_score` (due decimali).
**Sessione di ascolto**: `ApplauseAnalyzerController.begin(token, durata)` / `finish()` e il segnale
`sessionFinished(token, esito, voto, secondi)`, emesso una volta sola con esito `valid | empty | cancelled`.
Il valore 1,0 non dice nulla sulla validita': conta solo l'esito. La gara accetta solo la sessione che ha avviato (token).
**Salvataggio**: `~/.fab_sound_clap_meter/race.json` (scrittura atomica ad ogni modifica). Se il programma si chiude durante
una misura, questa viene registrata come annullata alla riapertura.
**Grafica** (`ui/qml/manche/`): `RunPage` (conduzione), `BoardPage` (tabellone), `ConfigPage` (configurazione) e i loro
componenti. I colori vengono dalla palette (`Theme.colors`, ruoli `personA`, `personB`, `good`, `warn`, `danger`).
