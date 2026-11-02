# Applausometro – Guida Operatore

Il numero grande è il voto da **1 a 10**. Sale con l'applauso e scende piano quando smette.
Accanto trovi il voto più basso (**Min**) e più alto (**Max**) raggiunti, con il pulsante **Azzera min/max**, e l'**Applause score**.

In alto ci sono due schede: **Configurazione** (questa guida) e **Manche** (in lavorazione). Le sezioni si dispongono in colonne secondo la larghezza della finestra e si chiudono con un clic sul titolo.

## 1. Ingressi audio (colonna di sinistra)

Ogni microfono ha una scheda con questi comandi:

| Comando | A cosa serve |
|---|---|
| **Interruttore** | Accende o spegne questo microfono. Se è spento, non conta nel voto. |
| **Menu dispositivo** | Sceglie quale microfono usare (USB o quello del PC). |
| **Peso** | Dice quanto questo microfono conta nel voto (da 1 a 10). |
| **Rimuovi** | Toglie il microfono. Ne deve restare almeno uno. |
| **Barra verde** | Mostra il volume in dB in tempo reale. La riga blu è la soglia dell'1, la riga rossa quella del 10. |

Il pulsante **Aggiungi ingresso** aggiunge un altro microfono.

### Come funziona il Peso

Il peso è un'**importanza**. Non conta il numero da solo, ma il confronto tra i microfoni.

- Con **un solo microfono** il peso non cambia niente.
- Con **più microfoni**, ognuno conta in proporzione al suo peso.

Esempio: microfono A con peso 8 e microfono B con peso 2. A conta l'80%, B il 20%.
Peso 1 è il minimo: quel microfono conta pochissimo.

Un microfono con peso basso, ma molto vicino a un applauso forte, può comunque farsi sentire: il calcolo usa la potenza del suono, non solo il numero.

## 2. Calibrazione (colonna di destra)

La calibrazione insegna all'app due cose: **quanto è forte il silenzio della sala (= voto 1)** e **quanto è forte un applauso fortissimo (= voto 10)**. Tutto quello che sta in mezzo viene distribuito tra 1 e 10.

Scegli il tipo dal menu in alto:

| Tipo | Come funziona |
|---|---|
| **Semplice** | Il voto cresce in modo regolare tra le due soglie. La più facile da usare. |
| **Con curva non lineare** | Come la semplice, ma puoi rendere il voto più generoso o più severo (vedi cursore Curva). |
| **Manuale** | Niente pulsanti di cattura. Guardi i dB in tempo reale e imposti tu le due soglie con i cursori. |

### I comandi della calibrazione

| Comando | A cosa serve |
|---|---|
| **Barra dei dB** | Il volume attuale, con la riga blu (1) e la riga rossa (10). |
| **Cattura fondo (=1)** | Ascolta la sala per 3 secondi e fissa la soglia dell'**1**. Premilo con il pubblico presente, ma senza applausi né musica. |
| **Cattura applauso (=10)** | Ascolta per 3 secondi e fissa la soglia del **10**. Premilo mentre il pubblico fa un applauso forte e continuo. |
| **Soglia 1** | Cursore per spostare a mano la soglia dell'1. Sotto questo volume il voto resta 1. |
| **Soglia 10** | Cursore per spostare a mano la soglia del 10. Sopra questo volume il voto resta 10. |
| **Curva (esponente)** | Solo nella modalità con curva. Sotto 1 il voto è più generoso, sopra 1 è più severo, 1 è come la semplice. |

I pulsanti di cattura compaiono solo nelle modalità **Semplice** e **Con curva**.

### Spike filter (spunta in fondo alla calibrazione)

Toglie i **picchi brevi** di volume, come un colpo sul microfono, un urlo o un battito isolato, che altrimenti alzerebbero il voto per un attimo. Gli applausi veri restano.

| Regolatore | A cosa serve |
|---|---|
| **Soglia spike** | Quanto un picco deve superare il volume normale per essere considerato spike (12 dB all'inizio). Più bassa = toglie di più. |
| **Durata massima spike** | Un rumore forte che dura **meno** di questo tempo (300 ms all'inizio) viene tolto. Se dura **di più**, è considerato applauso e resta. |
| **Ritardo della misura** | Non si regola: è un'informazione. Il filtro deve "guardare avanti" per decidere, quindi il voto arriva un po' in ritardo (0,5 s all'inizio). |

Due cose da sapere:
- I battiti ravvicinati di un applauso restano. Un battito **isolato**, con almeno 0,2 s di calma prima e dopo, viene invece trattato come spike.
- Le barre dei singoli microfoni mostrano sempre il volume **vero**. Il filtro agisce sul volume totale (barra della calibrazione) e quindi sul voto.

## 3. Applause Algorithm

Sceglie come calcolare l'**Applause score** (da 1 a 10), che compare anche sullo schermo del pubblico. Ogni algoritmo ha i suoi regolatori.

**Weighted Sliding Window Algorithm**: guarda solo gli ultimi secondi (finestra mobile) e unisce tre cose: quanto è stato forte l'applauso in media (50%), quanto è stato forte nei momenti migliori (30%) e per quanto tempo è rimasto forte (20%).

| Regolatore | A cosa serve |
|---|---|
| Durata finestra mobile | Quanti secondi guardare (4 all'inizio). Corta = reagisce in fretta. Lunga = più stabile. |
| *Advanced settings* (si apre con un clic, chiusa all'inizio): | |
| Frequenza di aggiornamento | Ogni quanto ricalcola il voto (0,5 s). |
| Soglia di costanza | Voto minimo per contare come "applauso forte" (6). |
| Soglia di attivazione | Sotto questo voto l'applauso non è ancora iniziato (3). |
| Tempo di stabilizzazione | Secondi iniziali da ignorare (0,5 s). |
| Pesi (media, picco, costanza) | Quanto conta ciascuna delle tre parti. Non serve che facciano 100. |

L'analizzatore è **fermo** finché non lo avvii dalla scheda **Manche** con **Start applause analyzer**. Con **Stop applause analyzer** si ferma e dà il **voto finale**: la media degli ultimi 2,5 secondi, così un attimo rumoroso non decide il risultato.

## 4. Schermo del pubblico

| Comando | A cosa serve |
|---|---|
| **Stile pubblico** | Cambia la grafica dello schermo del pubblico. |
| **Mostra / Nascondi pubblico** | Apre o chiude la finestra del pubblico. |
| **Schermo intero** | Mette la finestra del pubblico a schermo intero (anche con doppio click o tasto F11). |

## In breve, per iniziare

1. Scegli il microfono e controlla che la barra verde si muova.
2. Premi **Cattura fondo** con la sala in silenzio.
3. Fai fare un applauso forte e premi **Cattura applauso**.
4. Prova con qualche applauso e, se serve, ritocca le soglie.

Non cambiare più microfono, peso o soglie durante la gara: tutti i concorrenti devono essere misurati nello stesso modo.
