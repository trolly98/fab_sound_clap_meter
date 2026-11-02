# Applausometro per la Gara di Bugie
## Funzionamento atteso

### 1. Obiettivo

Realizzare un'applicazione per PC che misuri gli applausi del pubblico e restituisca un voto da **1 a 10, con un decimale**. Il voto deve premiare soprattutto l'intensità; la durata deve avere un'influenza secondaria. L'applicazione deve funzionare senza connessione Internet.

### 2. Preparazione della serata

L'operatore inserisce nome dell'evento, data, luogo e nomi dei due concorrenti. Collega e seleziona un microfono USB, oppure un ingresso della scheda audio, e verifica il livello ricevuto.

Una breve configurazione guidata dovrà raccogliere informazioni pratiche sullo spazio: ambiente chiuso o aperto, distanza indicativa del microfono dal pubblico, numero di persone, rumore e riverbero. Le risposte serviranno a proporre impostazioni iniziali; tutte le regolazioni dovranno restare modificabili dall'operatore.

Prima della gara si eseguiranno due calibrazioni:

- **Rumore di fondo → riferimento dell'1:** ascolto della sala con il pubblico presente, senza persone sul palco, annunci o musica. Il normale chiacchiericcio non microfonato del pubblico costituisce il fondo da escludere dalla valutazione. Da questa misura il programma ricaverà l'estremo inferiore della scala, con un margine per le normali fluttuazioni.
- **Applauso forte → riferimento del 10:** ascolto di un applauso forte e sostenuto richiesto allo stesso pubblico, con microfono e impianto nella disposizione prevista per la gara.

La calibrazione deve segnalare se fondo e applauso sono troppo simili o se il segnale è saturo. Posizione del microfono, guadagno e parametri di voto devono restare uguali per entrambi i concorrenti; un'eventuale ricalibrazione deve essere esplicita e registrata.

Le regolazioni dovranno permettere di adattare l'ascolto a sale diverse, intervenendo su guadagno digitale, frequenze analizzate, riduzione del fondo e attenuazione delle code di riverbero. Dovrà essere possibile aggiungere un secondo microfono, per ascoltare un'altra zona del pubblico oppure un disturbo da compensare.

### 3. Svolgimento di una votazione

1. L'operatore seleziona manche, eventuale turno e concorrente.
2. Quando il concorrente termina la bugia e inizia l'applauso, l'operatore avvia subito l'ascolto.
3. La misura segue la modalità scelta: **tempo fisso**, uguale per tutti, oppure **avvio e arresto manuali**, con l'operatore che decide quando concludere l'ascolto.
4. Al termine il programma calcola il voto, lo salva e lo visualizza sullo schermo del computer, associato al concorrente e alla manche selezionati.

Durante monologhi, presentazioni e musiche il programma resta in attesa e non assegna voti. L'avvio di ciascuna misurazione resta sotto il controllo dell'operatore. Tutte le visualizzazioni sono destinate alla regia.

### 4. Criterio del voto

L'intensità va valutata rispetto al fondo della sala, senza basarsi sul solo picco massimo. Un singolo colpo o urlo non deve determinare da solo il risultato. Nella modalità a tempo fisso la valutazione deve considerare l'intera finestra, comprese le pause.

**Finestra iniziale proposta per la modalità a tempo fisso: 5 secondi.**

Il fondo della sala, definito nella prima calibrazione, corrisponde al riferimento inferiore della scala; l'applauso forte di riferimento al massimo. La risposta deve distinguere in modo progressivo applausi deboli, medi e forti. La stessa registrazione, con gli stessi parametri, deve restituire lo stesso voto.

### 5. Manche e risultato finale

La scaletta comprende:

- **Il Bug-io:** un voto per concorrente.
- **Bazze Volanti:** due voti per concorrente.
- **Il Tribunale:** un voto per concorrente dopo il proprio turno di difesa.
- **La Grande Balla:** un voto per concorrente.

Sono previste dieci misurazioni. L'operatore deve poter modificare l'ordine o saltare una manche.

Per Bazze Volanti si usa la media dei due turni, così ogni manche ha lo stesso peso. Il totale è la somma dei quattro voti di manche. Il tabellone deve mostrare i voti per manche e il totale progressivo di ciascun concorrente, segnalando voti mancanti e parità.

### 6. Interfaccia e salvataggio

La schermata di regia deve mostrare chiaramente concorrente, manche, stato della misura, livello audio, tempo trascorso o rimanente, voto e riepilogo della gara. Servono comandi semplici per configurare la sala, calibrare, avviare, fermare e annullare una misurazione. I nomi dei concorrenti devono essere modificabili.

Ogni risultato valido deve essere salvato automaticamente e recuperabile dopo una chiusura del programma. Deve essere possibile esportare il riepilogo della serata.

Durante le misurazioni dovrà essere possibile registrare localmente l'audio ricevuto, insieme ai parametri e al risultato, per analizzare eventuali disturbi. L'opzione dovrà poter includere anche le calibrazioni. Le registrazioni non devono rallentare il calcolo del voto.
