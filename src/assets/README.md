# Icona dell'app

Metti qui il file **`icon.png`**. Viene usato per:
- la barra del titolo delle finestre (accanto ai tasti chiudi / riduci a icona)
- la barra delle applicazioni (Windows) o il Dock (macOS)

Come deve essere:
- PNG **quadrato**, consigliato **512 x 512** (minimo 256 x 256)
- sfondo **trasparente**
- soggetto ben visibile anche a 32 x 32 pixel

Se il file manca, l'app parte lo stesso con l'icona di sistema.

## Solo se crei un eseguibile (PyInstaller o simili)
L'icona del file .exe / .app non arriva dal PNG:
- Windows: converti il PNG in `icon.ico` (multi-risoluzione) e usa `--icon assets/icon.ico`
- macOS: converti in `icon.icns` e usa `--icon assets/icon.icns`
