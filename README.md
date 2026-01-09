# DVB-T Standalone Player

## Introduzione
Questo progetto presenta un DVB-T Standalone Player con interfaccia grafica (GUI) sviluppata in Python utilizzando il framework PyQt6. Permette agli utenti di scansionare, gestire e riprodurre canali DVB-T direttamente sul proprio computer, integrando strumenti di sistema come `dvbv5-scan`, `dvbv5-zap` e `mpv` per la sintonizzazione e la riproduzione video.

## Spiegazione
Il `DVB-T Standalone Player` mira a fornire un'applicazione user-friendly per la fruizione della televisione digitale terrestre. A differenza delle soluzioni tradizionali che spesso richiedono configurazioni complesse o software proprietari, questo player offre un'interfaccia semplice per:
*   Ricercare automaticamente i canali DVB-T disponibili nella propria zona.
*   Gestire una lista di canali con funzionalità di ricerca rapida.
*   Riprodurre i canali sintonizzati all'interno dell'applicazione o in una finestra MPV esterna in fullscreen.

L'applicazione gestisce in modo efficiente i file di configurazione dei canali (`channels.conf` e `it-All`) e si occupa della logica di sintonizzazione e riproduzione attraverso l'esecuzione di comandi esterni, offrendo una soluzione completa per gli appassionati di DVB-T.

## Funzionamento
L'applicazione `main.py` opera come segue:
1.  **Interfaccia Utente (GUI)**: Basata su PyQt6, presenta una finestra principale divisa in due sezioni: una sidebar sinistra con la lista dei canali e una barra di ricerca, e un'area video a destra per la riproduzione.
2.  **Caricamento Canali**: Al primo avvio o dopo una scansione, carica i nomi dei canali dal file `channels.conf`. Se il file non esiste, invita l'utente ad avviare una scansione.
3.  **Scansione Canali**: L'utente può avviare una "Nuova Scansione". L'applicazione scarica (`curl`) il file di tuning `it-All` (se non presente) e utilizza `dvbv5-scan` per ricercare i canali disponibili, salvandoli in `channels.conf`. Durante la scansione, una barra di progresso indica l'attività.
4.  **Filtro Canali**: Un campo di ricerca permette di filtrare rapidamente la lista dei canali visualizzati.
5.  **Riproduzione Canale**:
    *   Facendo doppio clic su un canale nella lista, l'applicazione utilizza `dvbv5-zap` per sintonizzarsi sul canale e invia il flusso video (`fd://0`) a `mpv`, che lo riproduce nell'area video integrata nella GUI.
    *   È disponibile una scorciatoia `CTRL+F` che lancia la riproduzione in una finestra `mpv` esterna e in modalità fullscreen, utile per una visione immersiva.
6.  **Deduplicazione Canali**: Dopo una scansione, una funzione interna `_deduplicate_channels_file` rimuove le voci duplicate dal `channels.conf` per mantenere la lista pulita.
7.  **Gestione Processi Esterni**: L'applicazione gestisce i processi `dvbv5-zap` e `mpv` avviandoli e terminandoli all'occorrenza, garantendo che non ci siano processi orfani.

## Istruzioni per avviarlo

### Prerequisiti
Prima di iniziare, assicurati di avere installati i seguenti componenti sul tuo sistema Linux:
*   **Python 3**: La versione 3.x di Python.
*   **PyQt6**: Il framework per la GUI.
*   **dvbv5-utils**: Un pacchetto che include `dvbv5-scan` e `dvbv5-zap`, necessari per la scansione e la sintonizzazione dei canali DVB. Questo è tipicamente fornito dal tuo gestore di pacchetti Linux (es. `sudo apt install dvb-tools` su Debian/Ubuntu, `sudo dnf install dvb-apps` su Fedora, etc.).
*   **MPV Player**: Un lettore multimediale versatile utilizzato per la riproduzione video. (es. `sudo apt install mpv` o `sudo dnf install mpv`).
*   **curl**: Utilità da riga di comando per il trasferimento dati, usata per scaricare `it-All`. (es. `sudo apt install curl` o `sudo dnf install curl`).
*   **Tuner DVB-T**: Un tuner hardware DVB-T funzionante e configurato correttamente sul tuo sistema.

### Installazione
1.  **Clona il repository (se applicabile)**:
    ```bash
    git clone https://github.com/Ak1r4Yuk1/DVB-T-Player
    cd DVB-T-Player
    ```
    Se hai già i file localmente, naviga semplicemente nella directory del progetto.

2.  **Installa le dipendenze Python**:
    ```bash
    pip install -r requirements.txt
    ```

### Configurazione
*   Assicurati che il tuo tuner DVB-T sia riconosciuto dal sistema e che i driver siano correttamente installati.
*   Il player cercherà automaticamente di scaricare il file `it-All` per la scansione. Non è necessaria una configurazione manuale iniziale di questo file.

### Esecuzione
Per avviare il DVB-T Standalone Player, esegui lo script `main.py` dal tuo terminale:
```bash
python main.py
```
L'applicazione si aprirà, permettendoti di iniziare la scansione dei canali e la loro riproduzione.
