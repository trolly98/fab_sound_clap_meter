# fab_sound_clap_meter

DB Meter: multiple audio inputs -> dB -> score 1.0-10.0.

## Run
    python -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    python src/main.py

Test: `python -m pytest tests`

## Architecture
- `domain/`          Pure logic, independent of Qt: weighted mixer, scale mapper, calibration modes, smoothing
- `audio/`           QtMultimedia + NumPy: handling input streams and measuring dBFS levels
- `application/`     `ClapMeterEngine` (facade for QML) and `ChannelController` (for a single input)
- `infrastructure/`  Saving settings to JSON, style discovery
- `ui/qml/`          Operator window and public-facing window

## Multi-input formula
P = sum(w_i * 10^(dB_i/10)) / sum(w_i);  dB = 10*log10(P)   (pesi 1-10 for each input)

## New style for the UI
Copy `ui/qml/styles/BarStyle.qml` to `<Name>Style.qml` and redesign it; it will automatically appear in the selector.
The style receives a `meter` object (containing `score`, `scoreText`, `combinedDb`, `floorDb`, `peakDb`, `channels[...]`, etc.).
