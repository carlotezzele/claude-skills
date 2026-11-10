---
name: "homework"
description: Trova il documento di un compito (homework) tra i file condivisi su Google Classroom e lo compila direttamente. Usa questa skill ogni volta che l'utente parla di compiti, consegne, esercizi, relazioni, temi, ricerche, "devo consegnare", "il prof ha assegnato", "su Classroom", o chiede di fare, completare o scrivere un lavoro scolastico, anche senza nominare un file o la skill. Prima controlla se il file di cui si parla in chat è tra quelli condivisi su Classroom (Drive); se non c'è chiede nome o link del documento. Se tutta la consegna è già nel documento parte subito a lavorare; altrimenti aspetta il materiale e le indicazioni su cosa scrivere.
---

# Homework

Serve a far arrivare un compito dalla chat al documento giusto con meno passaggi possibile: trova il file, capisce se ha già tutto il necessario, e scrive la consegna direttamente nel documento.

I file di Classroom vivono su Google Drive (gli allegati dei prof sono "Condivisi con me", le copie dello studente stanno in `Classroom/<nome corso>`). Per questo la ricerca passa da Drive, a meno che sia disponibile un connettore Classroom vero e proprio: in quel caso usalo per primo, perché dà anche titolo del compito, corso e scadenza.

## 1. Capire di che compito si parla

Ricava dalla chat: materia, titolo o argomento, prof o corso se citati, scadenza. L'utente lavora su un documento alla volta. Può dirti di prendere la consegna o del materiale da altri documenti, ma si modifica sempre e solo un documento: quello della consegna. Se ha già dato materiale, una griglia di valutazione o detto cosa scrivere, tienilo da parte: ti serve ai punti 3 e 4. Non chiedere nulla che sia già nella conversazione.

## 2. Cercare il documento tra i file di Classroom

Prima della prima chiamata a Drive, Docs o Sheets leggi la skill `google-workspace` e carica gli strumenti Google necessari (su alcune superfici sono differiti: cercali con `tool_search`).

Cerca con 1-3 parole chiave prese dalla chat (materia, argomento, nome del compito), provando in quest'ordine:

1. `sharedWithMe = true and title contains '<parola>'`
2. `title contains '<parola>'` senza altri filtri, e la cartella `Classroom`
3. `fullText contains '<parola>'` se i titoli non bastano
4. `list_recent_files` ordinati per ultima modifica, se la ricerca per parole non porta a nulla

La ricerca Drive usa `title`, non `name`. Segui il token di pagina successiva finché non finisce e scarta i duplicati.

Poi decidi:

- **Un candidato chiaro**: procedi. Nominalo nella risposta finale con il link.
- **Più candidati plausibili**: una sola domanda breve con le opzioni (titolo, proprietario, data).
- **Nessun candidato**: scrivi un solo messaggio breve, tipo "Non lo trovo tra i file condivisi su Classroom: mi dai il nome o il link del documento?". Dal link ricavi l'ID del file (il pezzo dopo `/d/`).

Attenzione a originale e copia. L'originale del prof è di sola lettura per lo studente; con "crea una copia per ogni studente" la copia modificabile è in `Classroom/<corso>`. Controlla i permessi con `get_file_metadata` o `get_file_permissions` prima di scrivere. Se trovi solo l'originale, chiedi il link alla copia dell'utente: non modificare l'originale e non creare copie nuove senza chiedere.

Se il connettore Google Docs non è attivo, dillo in una riga e chiedi se attivarlo o se preferisce un testo da incollare a mano. Non costruire file alternativi di tua iniziativa.

## 3. Leggere il documento e scegliere la modalità

Leggi il documento con Drive `read_file_content` (con `includeComments: true`) per capire il contenuto, e tieni a mente il testo originale: serve per tornare indietro (vedi punto 4). Prima di modificare, leggi `references/docs.md` della skill `google-workspace`.

**Modalità A, parti subito.** La consegna è tutta nel documento: ci sono testo, domande o esercizi, e quello che serve per rispondere o è nel documento stesso o è conoscenza generale della materia. Non fare domande: scrivi.

**Modalità B, aspetta.** Manca qualcosa che solo l'utente può dare: il documento è vuoto o è solo un modello, rimanda a un libro, un testo da analizzare, un file o un video che non hai, oppure l'utente ha detto in chat che ti darà il materiale. Chiedi in un solo messaggio il materiale e cosa vuole che scriva nel documento. Quando arrivano, scrivi.

**Caso misto.** Se una parte è fattibile e una no, fai subito la parte fattibile e chiedi il resto nello stesso messaggio finale.

## 4. Scrivere nel documento

**Fonti e materiale.** Se la consegna e il materiale dati dall'utente bastano, usa solo quelli: niente ricerche esterne. Cerca fuori solo se mancano informazioni necessarie, o se qualcosa di quello che dice l'utente è sbagliato; in quel caso scrivi nel documento la versione corretta e segnalalo in una riga nella risposta.

**Griglia di valutazione.** L'utente la dà riassunta in chat. Scrivi tenendola davanti e, alla fine, controlla che ogni voce sia coperta.

**Stile: non deve sembrare scritto da un'AI.** Scrivi come uno studente preparato, non come un assistente.
- Se l'utente ha dato un testo suo, imita lessico, lunghezza delle frasi e modo di collegare le idee.
- Parole semplici e concrete. Frasi di lunghezza diversa, alcune brevi. Dettagli specifici presi dal materiale o dalla materia, non affermazioni generiche.
- Evita le formule tipiche da AI: aperture e chiusure d'effetto, "In conclusione", "è importante sottolineare", "nel panorama di", "un ruolo cruciale", catene di "inoltre/pertanto", triplette simmetriche, riassunto finale che ripete quanto detto, tono enfatico o promozionale, trattini lunghi usati come tic.
- Niente elenchi puntati, grassetti o titoletti se la consegna non li chiede. Mantieni font e formattazione già presenti nel documento.

**Lunghezza.** Testi medi, a meno che la consegna indichi un limite: in quel caso rispettalo. Niente bibliografia se non è richiesta.

**Formato delle risposte.** Scegli in base a com'è fatto il documento.

*Elenco di domande o esercizi* (per esempio una serie di query SQL o di problemi): scrivi le risposte sotto, numerate come la consegna, nella forma `1)`, `2)`, `3)`, ognuna su una riga a sé seguita dalla risposta, con una riga vuota tra l'una e l'altra. Esempio:

```
1)
SELECT Marca, AVG(Prezzo) AS PrezzoMedio
FROM Automobili
GROUP BY Marca
HAVING PrezzoMedio > 20000

2)
SELECT Marca, COUNT(Modello) AS NumeroModelli
FROM Automobili
GROUP BY Marca
```

*Documento con molte sezioni e più parti*: la risposta va subito sotto la sua domanda, che resta dov'è con la sua numerazione (`1.`, `2.`, `3.`). Una riga vuota dopo la domanda, poi la risposta in un paragrafo, senza etichette né titoletti. Esempio:

```
1. Perché non basta aspettare processori sempre più veloci?

Perché la velocità di un processore non può crescere all'infinito: i componenti non si possono rimpicciolire senza limite e il calore prodotto diventa ingestibile.

2. Come potresti far collaborare più processori sullo stesso calcolo?

Dividendo il calcolo in tante parti, una per processore, che lavorano contemporaneamente.
```

In entrambi i casi non toccare il testo delle domande e non aggiungere altro: niente introduzioni, titoli o commenti.

**Codice** (Java, JavaScript, concorrenza, sistemi operativi): scrivi solo il codice, in carattere a spaziatura fissa, indentato, con qualche commento semplice. Niente output, test o spiegazioni nel documento. Se puoi eseguirlo, provalo tu prima di scriverlo, perché deve compilare e girare davvero.

**Matematica**: Docs non ha LaTeX, quindi scrivi le formule in notazione leggibile (x², √x, ∫, lim) e mostra i passaggi se la consegna chiede lo svolgimento.

**Niente invenzioni**: non inventare citazioni, numeri di pagina o fonti.

**Come scrivere**
- Stesso file, stesso link. Modifica in place con l'editor Docs. Non cancellare né riscrivere la consegna o altri testi del prof: scrivi sotto ogni richiesta o negli spazi previsti.
- Invia ogni batch con il `revisionId` di una lettura fatta dopo l'ultima scrittura, tutto un passo logico in un solo batch.
- Rileggi il documento dopo la scrittura e controlla punto per punto che ogni richiesta della consegna sia coperta e che i vincoli siano rispettati. Correggi prima di rispondere.

**Tornare indietro.** Non salvare copie di backup: l'utente può usare la cronologia versioni di Docs. Finché la sessione resta aperta, ricordati la versione originale del documento letta al punto 3 e, se l'utente chiede di ripristinarla, riscrivila nello stesso file.

## 5. Risposta in chat

Breve: il link al documento (titolo come link, dentro una frase) e, solo se serve, una riga su ciò che manca o va controllato. Niente elenco di ciò che hai cambiato né spiegazioni del lavoro. Niente domande di ripasso, a meno che l'utente le chieda.

## Preferenze di Carlo

- Lingua: italiano, tono conciso.
- Un documento alla volta; si modifica solo quello.
- Scrittura diretta nel documento, senza bozza in chat prima.
- Matematica: compila direttamente, come le altre materie.
- File non Google Doc (.docx, PDF): da definire; nel dubbio chiedi.
