import os
import base64
import urllib.parse
import streamlit as st
from fpdf import FPDF
from datetime import datetime

try:
    from PIL import Image
except ImportError:
    Image = None

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Analisi Trasformazione Digitale - Ago Infinity",
    page_icon="📊",
    layout="wide"
)

# --- STILE CSS PERSONALIZZATO ---
st.markdown("""
<style>
    [data-testid="stHeader"] {
        background: transparent;
    }
    .block-container {
        padding-top: 2.0rem !important;
        padding-bottom: 2rem !important;
    }
    .top-logos-bar {
        position: relative;
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 60px;
        padding: 16px 24px;
        border-radius: 10px;
        margin-top: 0px;
        margin-bottom: 18px;
        background:
            radial-gradient(circle at 22% 35%, rgba(125, 198, 245, 0.28) 0%, transparent 38%),
            radial-gradient(circle at 78% 65%, rgba(145, 210, 250, 0.22) 0%, transparent 42%),
            repeating-linear-gradient(
                135deg,
                rgba(255, 255, 255, 0.04) 0px,
                rgba(255, 255, 255, 0.04) 2px,
                transparent 2px,
                transparent 18px
            ),
            linear-gradient(125deg, #075c9e 0%, #0d72bd 48%, #165e96 100%);
        box-shadow: 0 4px 14px rgba(7, 92, 158, 0.22);
    }
    .top-logos-bar::before {
        content: "";
        position: absolute;
        inset: 0;
        background-image:
            radial-gradient(circle, rgba(255, 255, 255, 0.25) 1.5px, transparent 1.5px),
            radial-gradient(circle, rgba(255, 255, 255, 0.16) 2px, transparent 2px);
        background-size: 48px 48px, 84px 84px;
        background-position: 10px 12px, 32px 24px;
        pointer-events: none;
    }
    .top-logos-bar img.logo-item {
        position: relative;
        z-index: 1;
        height: 54px;
        width: auto;
        max-width: none;
        object-fit: contain;
        background-color: rgba(255, 255, 255, 0.96);
        padding: 6px 14px;
        border-radius: 7px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.14);
    }
    .header-box {
        background-color: #f4f7fa;
        border-left: 6px solid #1b4f72;
        padding: 18px 24px;
        border-radius: 6px;
        margin-bottom: 22px;
    }
    .header-title {
        color: #1b4f72;
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .header-subtitle {
        color: #2e4053;
        font-size: 17px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .meta-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 8px;
        font-size: 14px;
    }
    .meta-table td {
        padding: 6px 10px;
        border-bottom: 1px solid #d6eaf8;
    }
    .meta-label {
        font-weight: 700;
        color: #1b4f72;
        width: 220px;
    }
    .phase-header {
        background-color: #1b4f72;
        color: white;
        padding: 10px 15px;
        border-radius: 5px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .referente-box-title {
        font-weight: 700;
        color: #1b4f72;
        font-size: 15px;
        margin-bottom: 8px;
    }
    .mailto-btn {
        display: inline-block;
        width: 100%;
        text-align: center;
        background-color: #1b4f72;
        color: #ffffff !important;
        text-decoration: none !important;
        font-weight: 600;
        font-size: 14px;
        padding: 10px 16px;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 12px;
        box-sizing: border-box;
    }
    .mailto-btn:hover {
        background-color: #154360;
    }
    .zsicilia-info {
        font-size: 13px;
        line-height: 1.5;
        color: #2e4053;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONE HELPER PER IMMAGINI BASE64 ---
def get_image_base64(path: str) -> str:
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return ""

def get_image_width_for_height(path: str, target_h: float, fallback_w: float = 35.0) -> float:
    if Image is not None and os.path.exists(path):
        try:
            with Image.open(path) as im:
                w, h = im.size
                if h > 0:
                    return (w / h) * target_h
        except Exception:
            pass
    return fallback_w

# --- BARRA LATERALE (ELABORATA PRIMA DELL'INTESTAZIONE) ---
with st.sidebar:
    st.header("⚙️ Impostazioni Documento")
    studio_nome = st.text_input(
        "Denominazione Studio",
        value="",
        placeholder="Es. Studio Rossi & Associati"
    )
    versione_doc = st.text_input(
        "Data Documento",
        value="",
        placeholder="19/11/2026"
    )
    data_presa_visione = st.text_input(
        "Data Presa Visione (PDF)",
        value=datetime.now().strftime("%d/%m/%Y")
    )
    consenti_modifica_tobe = st.checkbox(
        "Consenti modifica colonne TO-BE e POST IMPLEMENTAZIONE",
        value=False
    )

    st.divider()
    st.info(
        "Compila i campi nella colonna **AS-IS (Situazione attuale)** per ciascuna fase. "
        "Le colonne **TO-BE** e **POST IMPLEMENTAZIONE** sono già precompilate."
    )

# --- DATI DINAMICI INTESTAZIONE ---
studio_display = studio_nome.strip() if studio_nome.strip() else "____________________________________"
versione_display = versione_doc.strip() if versione_doc.strip() else "_______________________"

HEADER_DATA = {
    "titolo": "PROGETTO DI TRASFORMAZIONE DIGITALE",
    "sottotitolo": f"Analisi dei processi studio professionale: {studio_display}",
    "piattaforma": "Ago Infinity – Zucchetti",
    "ambito": "Organizzazione dello studio, acquisizione documentale, contabilità, adempimenti fiscali e servizi al cliente",
    "redatto_da": "Consulente di Transformazione Digitale – Analisi Preliminare",
    "versione": versione_display,
    "finalita": "Definire il modello operativo futuro dello studio, individuando per ciascun processo la situazione attuale, il processo obiettivo e il risultato atteso a seguito dell'introduzione o dell'estensione delle funzionalità digitali collegate ad Ago Infinity."
}

# --- DATI PROCESSI DAL DOCUMENTO ---
PROCESS_DATA = [
    {
        "fase": "FASE 1 – Acquisizione del cliente e apertura della posizione",
        "processi": [
            {
                "nome": "Mandato professionale",
                "to_be": "Gestire il mandato con modello standard, raccolta digitale dei dati, firma elettronica ove prevista, protocollazione e archiviazione nella posizione cliente.",
                "post_impl": "Il mandato è associato alla scheda cliente e reperibile nell'archivio digitale; lo stato (da predisporre, inviato, firmato, completato) è monitorabile."
            },
            {
                "nome": "Antiriciclaggio (AML)",
                "to_be": "Digitalizzare la raccolta delle informazioni e dei documenti, le verifiche, la valutazione del rischio, gli aggiornamenti e le evidenze dei controlli, nel rispetto della normativa e delle procedure dello studio.",
                "post_impl": "Fascicolo antiriciclaggio strutturato, aggiornabile e tracciabile, con scadenze e controlli. Le valutazioni e gli adempimenti restano sotto responsabilità del professionista."
            },
            {
                "nome": "Creazione anagrafiche",
                "to_be": "Acquisire i dati da fonti ufficiali e documenti disponibili, con importazione o precompilazione ove supportata, controllo dei dati e validazione da parte dell'operatore.",
                "post_impl": "Anagrafiche create più rapidamente, con minori errori e dati coerenti reperendo le informazioni dalla amministrazione finanziaria."
            }
        ]
    },
    {
        "fase": "FASE 2 – Acquisizione documenti e dati contabili",
        "processi": [
            {
                "nome": "Acquisizione fatture elettroniche",
                "to_be": "Configurare il flusso di acquisizione delle fatture elettroniche tramite i canali e i servizi disponibili, con associazione automatica al cliente e regole di contabilizzazione.",
                "post_impl": "Le fatture vengono rese disponibili nell'ambiente di lavoro del cliente e avviate al processo di registrazione, con controlli sugli scarti e sulle anomalie."
            },
            {
                "nome": "Movimenti bancari / estratti conto",
                "to_be": "Attivare collegamenti bancari o flussi standard (ad esempio file bancari supportati), definendo frequenza, conti, causali, regole di abbinamento e gestione delle eccezioni.",
                "post_impl": "I movimenti finanziari vengono acquisiti in modo ricorrente e possono essere riconciliati con prima nota, incassi, pagamenti e partite aperte. Modulo AGO NEXT e ZPAY."
            },
            {
                "nome": "Import prima nota Excel del cliente",
                "to_be": "Definire un tracciato Excel standard dello studio, con campi obbligatori, codifiche, controlli preliminari e procedura di importazione.",
                "post_impl": "Il cliente produce un file conforme; lo studio importa i movimenti in modo ripetibile, riducendo attività di ricopiatura e rilavorazioni."
            },
            {
                "nome": "Utenza esterna per le aziende e utenza web",
                "to_be": "Abilitare utenti aziendali esterni con profili e permessi circoscritti, accesso autenticato e funzioni di caricamento documenti/dati e consultazione autorizzata.",
                "post_impl": "Ogni azienda dispone di un accesso dedicato; i documenti arrivano in un'area identificata e tracciata, senza accesso ai dati di altri clienti. Valutare utenza esterna contabile."
            },
            {
                "nome": "Caricamento saldi da contabilità esterna",
                "to_be": "Definire un tracciato condiviso per saldi e, se necessario, mastri o movimenti; mappare piano dei conti, esercizio, periodo e segni contabili; introdurre controlli di quadratura.",
                "post_impl": "Lo studio acquisisce i saldi in modo standardizzato per le attività fiscali, di bilancio e dichiarative, evitando la ricostruzione manuale. Va definito il livello di dettaglio necessario."
            }
        ]
    },
    {
        "fase": "FASE 3 – Adempimenti fiscali e acquisizione dati da fonti esterne",
        "processi": [
            {
                "nome": "Invii telematici e ricevute",
                "to_be": "Organizzare un flusso controllato di predisposizione, invio, acquisizione delle ricevute e aggiornamento dello stato della pratica, ove i servizi e le abilitazioni lo consentano.",
                "post_impl": "Lo stato degli invii è consultabile in modo centralizzato; ricevute ed esiti sono associati alla pratica, al cliente e al modello fiscale. Pubblicate in area riservata del cliente e app ZXCHANGE."
            },
            {
                "nome": "Scarico tributi dal Cassetto fiscale",
                "to_be": "Valutare i servizi di acquisizione automatica o assistita dei dati fiscali, definendo perimetro, deleghe, autorizzazioni e frequenza di aggiornamento.",
                "post_impl": "Le informazioni disponibili vengono acquisite e associate al cliente; lo studio può verificare versamenti e posizioni tributarie senza ripetere consultazioni manuali, direttamente in AGO Infinity."
            },
            {
                "nome": "Terreni e fabbricati – dati catastali",
                "to_be": "Acquisire, ove consentito, visure e dati catastali tramite servizi autorizzati, deleghe e procedure disponibili; prevedere controllo e aggiornamento dei dati.",
                "post_impl": "I dati immobiliari sono disponibili nel fascicolo cliente e riutilizzabili nei processi fiscali. L’acquisizione massiva/automatica avviene direttamente da procedura."
            },
            {
                "nome": "Utilizzo crediti IVA",
                "to_be": "Definire un processo periodico di acquisizione e controllo dei dati, con confronto tra credito dichiarato, credito disponibile e utilizzi/compensazioni rilevati.",
                "post_impl": "Lo studio dispone di un quadro aggiornato dei crediti IVA e delle relative movimentazioni, con evidenza delle differenze da verificare. L’interrogazione avviene all’interno della procedura."
            },
            {
                "nome": "Dichiarazioni precompilate",
                "to_be": "Valutare modalità di acquisizione delle precompilate tramite servizi autorizzati, deleghe e funzionalità disponibili; organizzare il controllo e l'integrazione dei dati.",
                "post_impl": "I dati acquisiti confluiscono nel processo dichiarativo e vengono sottoposti a verifica professionale prima dell'elaborazione e dell'invio."
            },
            {
                "nome": "File ISA",
                "to_be": "Standardizzare il recupero dei file ISA, l'associazione alla posizione fiscale e il passaggio dei dati al processo dichiarativo.",
                "post_impl": "I file ISA sono archiviati e associati al cliente/periodo d'imposta, con riduzione dei passaggi manuali e maggiore tracciabilità."
            }
        ]
    },
    {
        "fase": "FASE 4 – Servizi digitali e comunicazione con il cliente",
        "processi": [
            {
                "nome": "Portale cliente e App",
                "to_be": "Configurare un portale e un'app dedicati, con accesso sicuro, aree documentali, notifiche, richieste dello studio, scadenze e consultazione degli elaborati.",
                "post_impl": "Il cliente accede a un punto unico per documenti e comunicazioni; lo studio pubblica contenuti per singolo cliente e può monitorare consultazione e attività. Attivazione del portale Zucchetti e app ZXCHANGE."
            },
            {
                "nome": "Condivisione e raccolta documenti",
                "to_be": "Creare checklist per tipologia di cliente/adempimento, richieste documentali digitali, caricamento guidato e notifiche delle scadenze.",
                "post_impl": "La raccolta documentale è organizzata per pratica e periodo; si riducono solleciti ripetitivi e documenti dispersi."
            }
        ]
    },
    {
        "fase": "FASE 5 – Bilancio, deposito e pratiche extra",
        "processi": [
            {
                "nome": "Bilancio d'esercizio",
                "to_be": "Utilizzare i dati contabili presenti in Ago Infinity per predisporre bilancio, prospetti, scritture di assestamento e controlli; definire checklist di chiusura e validazione.",
                "post_impl": "Il processo di chiusura è standardizzato e tracciabile, con dati riutilizzati e controlli documentati."
            },
            {
                "nome": "Deposito bilancio",
                "to_be": "Integrare la predisposizione della pratica, i controlli formali, la generazione dei file e la gestione degli esiti secondo le funzionalità disponibili e le procedure camerali.",
                "post_impl": "La pratica di deposito è collegata al fascicolo cliente; documenti, ricevute ed eventuali richieste di correzione sono archiviati. Invio effettuato direttamente da procedura."
            },
            {
                "nome": "Pratiche extra / attività non ricorrenti",
                "to_be": "Creare una gestione strutturata delle pratiche extra: tipologia, incarico, responsabile, tempi, documenti, stato avanzamento, attività svolte e compenso.",
                "post_impl": "Ogni pratica extra è monitorabile dall'apertura alla chiusura, con responsabilità e documentazione associate. Possibilità di abbinare un trattamento economico ai fini di statistiche e fatturazione."
            }
        ]
    },
    {
        "fase": "FASE 6 – Reporting e analisi dei dati del cliente",
        "processi": [
            {
                "nome": "Report e analisi dati contabili",
                "to_be": "Definire un set di report standard per cliente e per settore: andamento economico, situazione patrimoniale, liquidità, scadenzari, costi/ricavi, indicatori e confronti periodici.",
                "post_impl": "Lo studio offre analisi ricorrenti e consultabili, con dati aggiornati e criteri omogenei. Le analisi devono distinguere dati contabili, stime e indicatori gestionali."
            }
        ]
    }
]

SEZIONI_TESTUALI = {
    "premessa": [
        "Il progetto mira a superare un'organizzazione basata su attività manuali, scambi documentali non strutturati e inserimenti ripetitivi, costruendo un flusso digitale integrato tra studio, cliente, istituti bancari e servizi dell'Amministrazione finanziaria.",
        "• Ridurre l'inserimento manuale dei dati e la duplicazione delle attività.",
        "• Centralizzare in Ago Infinity le informazioni anagrafiche, fiscali, contabili e documentali.",
        "• Automatizzare, ove tecnicamente possibile e autorizzato, acquisizione, elaborazione e riconciliazione dei dati.",
        "• Consentire ai clienti un canale digitale controllato per trasmettere documenti, consultare elaborati e interagire con lo studio.",
        "• Standardizzare i processi e rendere tracciabili responsabilità, controlli, scadenze ed esiti.",
        "• Valorizzare i dati contabili attraverso report e analisi periodiche."
    ],
    "modello": [
        "Per ogni area vengono distinti tre livelli:",
        "• AS-IS – situazione attuale: modalità operative oggi utilizzate dallo Studio, rilevate durante i colloqui e l'analisi sul campo.",
        "• TO-BE – processo obiettivo: come il processo dovrebbe essere organizzato, con regole, responsabilità e controlli definiti.",
        "• POST IMPLEMENTAZIONE – risultato atteso: come opererà lo Studio una volta configurate e collaudate le soluzioni.",
        "Nota metodologica: la disponibilità effettiva delle singole automazioni dipende da licenze, moduli, servizi attivi, autorizzazioni, tracciati e integrazioni disponibili per la specifica installazione di Ago Infinity."
    ],
    "flusso": [
        ("1. Onboarding", "Mandato, antiriciclaggio, anagrafica e abilitazioni."),
        ("2. Raccolta dati", "Fatture elettroniche, banca, prima nota, documenti e saldi esterni."),
        ("3. Elaborazione", "Contabilità, riconciliazioni, controlli e gestione delle anomalie."),
        ("4. Adempimenti", "Dichiarazioni, ISA, F24/tributi, invii telematici e ricevute."),
        ("5. Produzione", "Bilancio, deposito e pratiche professionali."),
        ("6. Condivisione", "Pubblicazione documenti e comunicazioni su portale/app."),
        ("7. Consulenza", "Report, indicatori e analisi periodiche per il cliente.")
    ],
    "requisiti": [
        "• Anagrafiche e codifiche: definire un archivio cliente univoco, criteri di denominazione, codici fiscali/partite IVA e collegamenti tra soggetti.",
        "• Sicurezza e profilazione: utenze nominative, autenticazione adeguata, ruoli distinti per personale interno e utenti esterni, principio del minimo privilegio.",
        "• Privacy e protezione dei dati: verificare basi giuridiche, informative, nomine, accordi con fornitori, conservazione e tempi di retention.",
        "• Deleghe e autorizzazioni: censire deleghe per Cassetto fiscale, servizi catastali e altri servizi dell'Amministrazione finanziaria; verificare scadenze e revoche.",
        "• Tracciabilità: registrare chi carica, modifica, valida, invia e pubblica documenti o dati, con data e ora.",
        "• Gestione eccezioni: prevedere code di errore, scarti, duplicati, dati mancanti, quadrature non coerenti e procedure di correzione.",
        "• Conservazione: distinguere archiviazione operativa, conservazione digitale a norma e semplice pubblicazione al cliente.",
        "• Continuità operativa: backup, ripristino, gestione indisponibilità dei servizi esterni e procedure alternative."
    ],
    "piano": [
        ("Step 0 – Assessment", "Mappatura dei processi reali, volumi, utenti, moduli Ago Infinity attivi, licenze, servizi esterni, banche e tracciati utilizzati.", "Matrice AS-IS validata, gap analysis e priorità."),
        ("Step 1 – Fondamenta", "Pulizia anagrafiche, standard documentali, profili utente, deleghe, mandato e fascicolo antiriciclaggio.", "Dati affidabili e governance degli accessi."),
        ("Step 2 – Ingressi digitali", "Fatture elettroniche, estratti conto, import prima nota Excel, utenze esterne e caricamento saldi.", "Riduzione dell'inserimento manuale e flussi di acquisizione standard."),
        ("Step 3 – Automazione fiscale", "Invii e ricevute, tributi, dati catastali, crediti IVA, precompilate e file ISA, nei limiti dei servizi autorizzati.", "Acquisizione assistita/automatica e fascicolo fiscale più completo."),
        ("Step 4 – Servizi al cliente", "Portale, app, pubblicazione documenti, notifiche e richieste documentali.", "Canale digitale unico tra studio e cliente."),
        ("Step 5 – Bilancio e pratiche", "Processi di chiusura, bilancio, deposito e gestione pratiche extra.", "Workflow standard e tracciabilità delle attività."),
        ("Step 6 – Reporting", "Definizione indicatori, modelli di report, frequenza e destinatari.", "Servizio di analisi continuativo e maggiore valore consulenziale.")
    ],
    "indicatori": [
        ("Tempo medio di apertura cliente", "Tempo tra conferimento incarico e posizione operativa completa."),
        ("Percentuale documenti acquisiti digitalmente", "Documenti ricevuti tramite canali strutturati rispetto al totale."),
        ("Tempo di registrazione contabile", "Tempo medio tra disponibilità del documento e registrazione/validazione."),
        ("Tasso di import senza errori", "File importati correttamente al primo tentativo sul totale dei file."),
        ("Riconciliazione bancaria", "Percentuale di movimenti abbinati automaticamente o con regole."),
        ("Ricevute telematiche archiviate", "Percentuale di invii con ricevuta acquisita e associata alla pratica."),
        ("Utilizzo portale/app", "Clienti attivi, accessi e documenti consultati/caricati."),
        ("Tempo di chiusura bilancio", "Tempo tra chiusura periodo e disponibilità del bilancio per revisione.")
    ],
    "fattibilita_esito": [
        "9. Attenzioni e perimetro di fattibilità: Le attività di acquisizione da Agenzia delle Entrate, Agenzia delle Entrate-Riscossione, Catasto, banche e altri soggetti terzi non devono essere considerate automaticamente disponibili. In fase di assessment occorre verificare, per ogni flusso, il servizio effettivamente utilizzabile, le deleghe, le credenziali/abilitazioni, le condizioni tecniche, i limiti di consultazione, i tracciati e le eventuali autorizzazioni del cliente. L'obiettivo è automatizzare raccolta, trasferimento, precompilazione e controlli ripetitivi, non sostituire la verifica del professionista.",
        "10. Esito atteso del progetto: Al termine del percorso lo studio disporrà di un modello operativo maggiormente digitale e integrato, nel quale Ago Infinity rappresenta il centro gestionale dei processi amministrativi, contabili e fiscali, mentre i canali di collegamento con clienti e soggetti esterni alimentano i flussi informativi."
    ]
}

# --- FUNZIONE SANIFICAZIONE TESTO PER PDF (FPDF latin-1) ---
def clean_text(text: str) -> str:
    if not text:
        return ""
    replacements = {
        "–": "-", "—": "-", "’": "'", "‘": "'",
        "“": '"', "”": '"', "•": "-", "…": "...",
        "€": "EUR"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")

# --- CLASSE GENERAZIONE PDF (FORMATO VERTICALE / PORTRAIT) ---
class ReportPDF(FPDF):
    def __init__(self, studio_header_txt="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.studio_header_txt = studio_header_txt

    def header(self):
        if self.page_no() == 1:
            return
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 110, 120)
        label_hdr = (
            f"PROGETTO DI TRASFORMAZIONE DIGITALE - {self.studio_header_txt} | Ago Infinity"
            if self.studio_header_txt
            else "PROGETTO DI TRASFORMAZIONE DIGITALE | Ago Infinity"
        )
        usable_w = self.w - self.l_margin - self.r_margin
        self.cell(usable_w, 5, clean_text(label_hdr), align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        self.set_y(-11)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        usable_w = self.w - self.l_margin - self.r_margin
        self.cell(usable_w, 7, f"Pagina {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.ln(3)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 11.5)
        self.set_text_color(27, 79, 114)
        usable_w = self.w - self.l_margin - self.r_margin
        self.cell(usable_w, 7, clean_text(title), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(27, 79, 114)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2.5)

def genera_pdf(meta_info, compiled_phases, data_firma, studio_raw, referente_info):
    pdf = ReportPDF(studio_header_txt=studio_raw, orientation="P", unit="mm", format="A4")
    pdf.set_margins(10, 10, 10)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    usable_w = pdf.w - pdf.l_margin - pdf.r_margin  # 190 mm su A4 Portrait

    # Loghi centrati in alto nella prima pagina del PDF senza barra blu sottostante
    has_left_logo = os.path.exists("logo_zsicilia.png")
    has_right_logo = os.path.exists("logo_zcspeople.png")
    if has_left_logo or has_right_logo:
        y_logo = pdf.get_y()
        logo_h = 12.0
        w1 = get_image_width_for_height("logo_zsicilia.png", logo_h, fallback_w=36.0) if has_left_logo else 0.0
        w2 = get_image_width_for_height("logo_zcspeople.png", logo_h, fallback_w=36.0) if has_right_logo else 0.0
        gap_w = 18.0
        total_w = w1 + w2 + (gap_w if (has_left_logo and has_right_logo) else 0.0)
        x_start = pdf.l_margin + (usable_w - total_w) / 2.0

        if has_left_logo:
            pdf.image("logo_zsicilia.png", x=x_start, y=y_logo, h=logo_h)
        if has_right_logo:
            x_r = x_start + w1 + (gap_w if has_left_logo else 0.0)
            pdf.image("logo_zcspeople.png", x=x_r, y=y_logo, h=logo_h)

        pdf.set_xy(pdf.l_margin, y_logo + logo_h + 4)

    # Intestazione principale documento
    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(27, 79, 114)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(usable_w, 9.5, clean_text(meta_info["titolo"]), fill=True, align="L", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(pdf.l_margin)
    pdf.set_fill_color(235, 245, 251)
    pdf.set_text_color(27, 79, 114)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.cell(usable_w, 8, clean_text(meta_info["sottotitolo"]), fill=True, align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Tabella Metadati Intestazione (190 mm totali)
    meta_rows = [
        ("Piattaforma di riferimento", meta_info["piattaforma"]),
        ("Ambito", meta_info["ambito"]),
        ("Redatto da", meta_info["redatto_da"]),
        ("Versione", meta_info["versione"]),
        ("Finalita del documento", meta_info["finalita"])
    ]
    label_w = 45
    val_w = usable_w - label_w

    for label, val in meta_rows:
        pdf.set_x(pdf.l_margin)
        y_row = pdf.get_y()
        lbl_txt = clean_text(label)
        val_txt = clean_text(val)

        pdf.set_font("Helvetica", "", 8.8)
        val_lines = pdf.multi_cell(val_w, 5, val_txt, split_only=True)
        row_h = max(6.5, len(val_lines) * 5.0 + 1.5)

        if y_row + row_h > pdf.h - pdf.b_margin:
            pdf.add_page()
            y_row = pdf.get_y()

        pdf.set_xy(pdf.l_margin, y_row)
        pdf.set_font("Helvetica", "B", 8.8)
        pdf.set_text_color(27, 79, 114)
        pdf.rect(pdf.l_margin, y_row, label_w, row_h)
        pdf.multi_cell(label_w, 5, lbl_txt, border=0)

        pdf.set_xy(pdf.l_margin + label_w, y_row)
        pdf.set_font("Helvetica", "", 8.8)
        pdf.set_text_color(30, 30, 30)
        pdf.rect(pdf.l_margin + label_w, y_row, val_w, row_h)
        pdf.multi_cell(val_w, 5, val_txt, border=0)

        pdf.set_xy(pdf.l_margin, y_row + row_h)

    # Sezione 1 e 2
    pdf.section_title("1. Premessa e obiettivi del progetto")
    pdf.set_font("Helvetica", "", 8.8)
    pdf.set_text_color(30, 30, 30)
    for riga in SEZIONI_TESTUALI["premessa"]:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(usable_w, 4.8, clean_text(riga))
        pdf.ln(0.8)

    pdf.section_title("2. Modello di lettura dell'analisi")
    for riga in SEZIONI_TESTUALI["modello"]:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(usable_w, 4.8, clean_text(riga))
        pdf.ln(0.8)

    # Sezione 3: Tabelle Processi su 190 mm in verticale
    pdf.add_page()
    pdf.section_title("3. Analisi dei processi per fase")

    col_widths = [32, 52, 53, 53]  # Totale = 190 mm
    headers = ["PROCESSO", "AS-IS\nSituazione attuale", "TO-BE\nCome deve essere", "POST IMPL.\nCome sara"]
    hdr_h = 9.0

    for fase_obj in compiled_phases:
        if pdf.get_y() > 245:
            pdf.add_page()

        pdf.ln(2.5)
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(214, 234, 248)
        pdf.set_text_color(27, 79, 114)
        pdf.cell(sum(col_widths), 7, clean_text(fase_obj["fase"]), border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "B", 7.8)
        pdf.set_fill_color(27, 79, 114)
        pdf.set_draw_color(27, 79, 114)
        pdf.set_text_color(255, 255, 255)

        y_start = pdf.get_y()
        x_start = pdf.l_margin
        for i, h in enumerate(headers):
            col_x = x_start + sum(col_widths[:i])
            pdf.rect(col_x, y_start, col_widths[i], hdr_h, style="DF")
            h_lines = h.split("\n")
            text_y = y_start + (hdr_h - len(h_lines) * 4.2) / 2.0
            pdf.set_xy(col_x, text_y)
            pdf.multi_cell(col_widths[i], 4.2, clean_text(h), border=0, align="C")

        pdf.set_draw_color(0, 0, 0)
        pdf.set_xy(x_start, y_start + hdr_h)

        pdf.set_text_color(20, 20, 20)
        for proc in fase_obj["processi"]:
            vals = [
                clean_text(proc["nome"]),
                clean_text(proc["as_is"] if proc["as_is"].strip() else "[Non compilato]"),
                clean_text(proc["to_be"]),
                clean_text(proc["post_impl"])
            ]
            line_heights = []
            for i, txt in enumerate(vals):
                pdf.set_font("Helvetica", "B" if i == 0 else "", 7.8)
                lines = pdf.multi_cell(col_widths[i], 4.2, txt, split_only=True)
                line_heights.append(len(lines) * 4.2 + 3)
            row_h = max(line_heights)

            if pdf.get_y() + row_h > pdf.h - pdf.b_margin:
                pdf.add_page()

            curr_y = pdf.get_y()
            curr_x = pdf.l_margin

            for i, txt in enumerate(vals):
                pdf.set_xy(curr_x + sum(col_widths[:i]), curr_y)
                pdf.set_font("Helvetica", "B" if i == 0 else "", 7.8)
                pdf.rect(curr_x + sum(col_widths[:i]), curr_y, col_widths[i], row_h)
                pdf.multi_cell(col_widths[i], 4.2, txt, border=0, align="L")

            pdf.set_xy(curr_x, curr_y + row_h)

    # Sezioni finali (4 - 10) su 190 mm in verticale
    pdf.add_page()
    pdf.section_title("4. Architettura funzionale del processo futuro")
    for step, desc in SEZIONI_TESTUALI["flusso"]:
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 8.8)
        pdf.cell(38, 5.5, clean_text(step), border=1)
        pdf.set_font("Helvetica", "", 8.8)
        pdf.cell(usable_w - 38, 5.5, clean_text(desc), border=1, new_x="LMARGIN", new_y="NEXT")

    pdf.section_title("5. Requisiti trasversali e controlli")
    pdf.set_font("Helvetica", "", 8.5)
    for req in SEZIONI_TESTUALI["requisiti"]:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(usable_w, 4.5, clean_text(req))
        pdf.ln(0.8)

    pdf.section_title("6. Piano di implementazione suggerito")
    p_widths = [38, 86, 66]  # Totale = 190 mm
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(27, 79, 114)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(p_widths[0], 6.5, "STEP", border=1, fill=True)
    pdf.cell(p_widths[1], 6.5, "ATTIVITA", border=1, fill=True)
    pdf.cell(p_widths[2], 6.5, "RISULTATO ATTESO", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(20, 20, 20)
    for s, att, ris in SEZIONI_TESTUALI["piano"]:
        vals = [clean_text(s), clean_text(att), clean_text(ris)]
        heights = []
        for i, v in enumerate(vals):
            pdf.set_font("Helvetica", "B" if i == 0 else "", 7.8)
            heights.append(len(pdf.multi_cell(p_widths[i], 4.2, v, split_only=True)) * 4.2 + 2.5)
        rh = max(heights)
        if pdf.get_y() + rh > pdf.h - pdf.b_margin:
            pdf.add_page()
        cy, cx = pdf.get_y(), pdf.l_margin
        for i, v in enumerate(vals):
            pdf.set_xy(cx + sum(p_widths[:i]), cy)
            pdf.set_font("Helvetica", "B" if i == 0 else "", 7.8)
            pdf.rect(cx + sum(p_widths[:i]), cy, p_widths[i], rh)
            pdf.multi_cell(p_widths[i], 4.2, v, border=0)
        pdf.set_xy(cx, cy + rh)

    pdf.section_title("7. Indicatori per misurare il risultato")
    for ind, mis in SEZIONI_TESTUALI["indicatori"]:
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.cell(65, 5.5, clean_text(ind), border=1)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.cell(usable_w - 65, 5.5, clean_text(mis), border=1, new_x="LMARGIN", new_y="NEXT")

    pdf.section_title("9 - 10. Perimetro di fattibilita ed esito atteso")
    pdf.set_font("Helvetica", "", 8.5)
    for blocco in SEZIONI_TESTUALI["fattibilita_esito"]:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(usable_w, 4.6, clean_text(blocco))
        pdf.ln(1.5)

    # Box Firma / Presa visione
    pdf.ln(5)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(90, 6, f"Data: {clean_text(data_firma)}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin)
    pdf.cell(90, 6, "PER PRESA VISIONE", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(7)
    pdf.set_x(pdf.l_margin)
    pdf.cell(90, 6, "________________________________________", new_x="LMARGIN", new_y="NEXT")

    # Box Referente di Studio in basso dopo presa visione
    pdf.ln(5)
    ref_rows = [
        ("Nome e Cognome Referente di Studio", referente_info.get("nome_cognome", "")),
        ("Cell:", referente_info.get("cell", "")),
        ("Email:", referente_info.get("email", "")),
        ("Num. Utenti di Studio", referente_info.get("num_utenti", ""))
    ]
    ref_lbl_w = 68
    ref_val_w = usable_w - ref_lbl_w
    ref_row_h = 6.5
    total_ref_h = len(ref_rows) * ref_row_h

    if pdf.get_y() + total_ref_h > pdf.h - pdf.b_margin:
        pdf.add_page()

    for lbl, val in ref_rows:
        y_r = pdf.get_y()
        pdf.set_x(pdf.l_margin)
        pdf.set_fill_color(244, 247, 250)
        pdf.set_draw_color(180, 195, 210)
        pdf.set_text_color(27, 79, 114)
        pdf.set_font("Helvetica", "B", 8.8)
        pdf.cell(ref_lbl_w, ref_row_h, clean_text(lbl), border=1, fill=True)

        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(30, 30, 30)
        pdf.set_font("Helvetica", "", 8.8)
        pdf.cell(ref_val_w, ref_row_h, clean_text(val), border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_y(y_r + ref_row_h)

    pdf.set_draw_color(0, 0, 0)
    return bytes(pdf.output())

# --- INTERFACCIA WEB STREAMLIT ---

# 0. BARRA LOGHI CENTRATA SU SFONDO BLU (ENTRAMBI DELLA STESSA ALTEZZA)
logo1_b64 = get_image_base64("logo_zsicilia.png")
logo2_b64 = get_image_base64("logo_zcspeople.png")

if logo1_b64 or logo2_b64:
    img1_html = f'<img class="logo-item" src="data:image/png;base64,{logo1_b64}" alt="Z Sicilia">' if logo1_b64 else ''
    img2_html = f'<img class="logo-item" src="data:image/png;base64,{logo2_b64}" alt="ZCS People">' if logo2_b64 else ''
    st.markdown(f"""
    <div class="top-logos-bar">
        {img1_html}
        {img2_html}
    </div>
    """, unsafe_allow_html=True)

# 1. INTESTAZIONE IN ALTO (Con campi dinamici popolati dalla barra a sinistra)
st.markdown(f"""
<div class="header-box">
    <div class="header-title">{HEADER_DATA['titolo']}</div>
    <div class="header-subtitle">{HEADER_DATA['sottotitolo']}</div>
    <table class="meta-table">
        <tr><td class="meta-label">Piattaforma di riferimento</td><td>{HEADER_DATA['piattaforma']}</td></tr>
        <tr><td class="meta-label">Ambito</td><td>{HEADER_DATA['ambito']}</td></tr>
        <tr><td class="meta-label">Redatto da</td><td>{HEADER_DATA['redatto_da']}</td></tr>
        <tr><td class="meta-label">Versione</td><td>{HEADER_DATA['versione']}</td></tr>
        <tr><td class="meta-label">Finalità del documento</td><td>{HEADER_DATA['finalita']}</td></tr>
    </table>
</div>
""", unsafe_allow_html=True)

# 2. COMPILAZIONE PROCESSI PER FASE
totale_processi = sum(len(f["processi"]) for f in PROCESS_DATA)
compilati = 0
compiled_phases = []

st.subheader("📋 Compilazione Analisi dei Processi per Fase")

for f_idx, fase_item in enumerate(PROCESS_DATA):
    st.markdown(f'<div class="phase-header">{fase_item["fase"]}</div>', unsafe_allow_html=True)

    c_proc, c_asis, c_tobe, c_post = st.columns([1.2, 2.2, 2.2, 2.2])
    c_proc.markdown("**PROCESSO**")
    c_asis.markdown("**AS-IS** *(Situazione attuale - da compilare)*")
    c_tobe.markdown("**TO-BE** *(Come deve essere)*")
    c_post.markdown("**POST IMPLEMENTAZIONE** *(Come sarà)*")
    st.divider()

    fase_compilata = {"fase": fase_item["fase"], "processi": []}

    for p_idx, proc in enumerate(fase_item["processi"]):
        col1, col2, col3, col4 = st.columns([1.2, 2.2, 2.2, 2.2])

        with col1:
            st.markdown(f"**{proc['nome']}**")

        with col2:
            as_is_val = st.text_area(
                label=f"AS-IS {proc['nome']}",
                value="",
                placeholder="Descrivi la situazione attuale dello studio...",
                height=135,
                key=f"asis_{f_idx}_{p_idx}",
                label_visibility="collapsed"
            )
            if as_is_val.strip():
                compilati += 1

        with col3:
            to_be_val = st.text_area(
                label=f"TO-BE {proc['nome']}",
                value=proc["to_be"],
                height=135,
                disabled=not consenti_modifica_tobe,
                key=f"tobe_{f_idx}_{p_idx}",
                label_visibility="collapsed"
            )

        with col4:
            post_val = st.text_area(
                label=f"POST {proc['nome']}",
                value=proc["post_impl"],
                height=135,
                disabled=not consenti_modifica_tobe,
                key=f"post_{f_idx}_{p_idx}",
                label_visibility="collapsed"
            )

        fase_compilata["processi"].append({
            "nome": proc["nome"],
            "as_is": as_is_val,
            "to_be": to_be_val,
            "post_impl": post_val
        })
        st.markdown("---")

    compiled_phases.append(fase_compilata)

# 3. AVANZAMENTO E GENERAZIONE PDF
st.progress(compilati / totale_processi, text=f"Processi AS-IS compilati: {compilati} su {totale_processi}")

st.subheader("📄 Esportazione Report PDF")
col_btn, col_box = st.columns([1, 2])

nome_file_studio = studio_nome.strip().replace(" ", "_") if studio_nome.strip() else "Studio_Professionale"

with col_box:
    with st.container(border=True):
        st.markdown('<div class="referente-box-title">Dati Referente di Studio</div>', unsafe_allow_html=True)
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            ref_nome_cognome = st.text_input(
                "Nome e Cognome referente di Studio",
                value="",
                placeholder="Es. Mario Rossi"
            )
            ref_email = st.text_input(
                "Email",
                value="",
                placeholder="Es. referente@studio.it"
            )
        with r_col2:
            ref_cell = st.text_input(
                "Cell",
                value="",
                placeholder="Es. 333 1234567"
            )
            ref_num_utenti = st.text_input(
                "Num. Utenti di Studio",
                value="",
                placeholder="Es. 12"
            )

referente_data = {
    "nome_cognome": ref_nome_cognome.strip(),
    "cell": ref_cell.strip(),
    "email": ref_email.strip(),
    "num_utenti": ref_num_utenti.strip()
}

with col_btn:
    pdf_bytes = genera_pdf(
        HEADER_DATA,
        compiled_phases,
        data_presa_visione,
        studio_nome.strip(),
        referente_data
    )
    st.download_button(
        label="⬇️ Scarica Report Completo in PDF",
        data=pdf_bytes,
        file_name=f"Analisi_Trasformazione_Digitale_{nome_file_studio}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )

    oggetto_mail = urllib.parse.quote(
        f"Analisi Trasformazione Digitale - {studio_nome.strip() if studio_nome.strip() else 'Studio Professionale'}"
    )
    corpo_mail = urllib.parse.quote(
        f"Buongiorno,\n\n"
        f"in allegato il report di analisi dei processi per lo studio: {studio_nome.strip() or 'N/D'}.\n"
        f"Referente di Studio: {ref_nome_cognome.strip() or 'N/D'}\n"
        f"Cell: {ref_cell.strip() or 'N/D'}\n"
        f"Email: {ref_email.strip() or 'N/D'}\n"
        f"Num. Utenti di Studio: {ref_num_utenti.strip() or 'N/D'}\n\n"
        f"Cordiali saluti."
    )
    mailto_href = (
        f"mailto:salvo.lampone@zsicilia.it"
        f"?cc=giacomo.berte@zsicilia.it"
        f"&subject={oggetto_mail}"
        f"&body={corpo_mail}"
    )

    st.markdown(f"""
    <a class="mailto-btn" href="{mailto_href}">invia email a ZSicilia SRL member of ZCS People</a>
    <div class="zsicilia-info">
        <strong>ZSICILIA SRL gruppo ZCS People</strong><br>
        Via Sampolo 3D – 90145 Palermo<br>
        P. Iva 07312960821<br>
        Referente Commerciale: salvo.lampone@zsicilia.it<br>
        Consulente Trasformazione Digitale: giacomo.berte@zsicilia.it
    </div>
    """, unsafe_allow_html=True)