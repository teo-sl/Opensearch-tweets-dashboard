# SISTEMA PER LA VISUALIZZAZIONE SU MAPPA DI GRANDI MOLI DI TWEET GEOLOCALIZZATI
## Progetto di Sistemi Distribuiti e Cloud Computing A.A. 2021/2022
### Autore: Teodoro Sullazzo matr. 235194

<hr>

# Indice
1. Introduzione
2. Pre-processing
3. Complex Cluster
    1. Logstash
    2. Opensearch
4. Mini-cluster
5. k8s-test
6. Configurazione di OpenSearch


# 1. Introduzione
Il presente lavoro ha come sup obiettivo la realizzazione di un sistema distribuito per la visualizzazione su mappa di grandi quantità di dati. Una più dettagliata descrizione sulla realizzazione del lavoro è disponibile nella relazione del progetto. Qui ci si concentrerà nella descrizione del codice, con una guida all'uso.


# 2. Pre-processing
A causa dell'assenza della geolocalizzazione sui dati forniti è stato necessario arricchire il dataset originale. Per fare questo si è ricorso al seguente dataset kaggle:

https://www.kaggle.com/datasets/manchunhui/us-election-2020-tweets

Da questo dataset sono state estratte le coordinate geografiche. Il codice per tale trasformazione è disponibile nel file "preprocessing.py" all'interno della cartella pre-processing. Qui vi sono due principali funzioni "importCoordinates" e "update". La prima permette di estrarre i geopoints dal dataset kaggle, tali dati vengono inseriti per comodità in un file "out.csv". La seconda funzione invece provvede ad aggiungere questi dati nel dataset fornito. A tal fine, viene scelta una coordinata a caso; questa viene poi opportunamente perturbata con un valore casuale per evitare una eccessiva concentrazione. Tutto ciò è facilmente comprensibile a partire dallo script python.

# 3. Complex Cluster
L'implementazione del cluster 4 nodi (dashboard + 2 nodi opensearch + logstash) è presente nella cartella complex-cluster. Qui vi sono altre due cartelle, una dedicata al deployment di logstash, e una per il resto del cluster .
## 3.1 Logstash
Il deployment di logstash comprende un file ove è indicato il comando docker per lanciarlo:

        docker run -it --rm --name logstash --net opensearch-cluster_opensearch-net -v ${PWD}\logstash\pipeline:/usr/share/logstash/pipeline -v ${PWD}\logs-data:/usr/share/logstash/logs-data opensearchproject/logstash-oss-with-opensearch-output-plugin:7.16.2

Qui è indicata la rete a cui il nodo deve collegarsi e i due volumi da montare. Nella pipeline è presente il file "logstash.conf", i.e. il file di configurazione della pipeline. In logs-data verranno inseriti invece i log affinché questi vengano automaticamente caricati da Logstash.

##  3.2 Opensearch
In questa cartella è definito il docker-compose per permettere il deployment del cluster: dashboard+nodi. A parte gli aspetti triviali come i volumi, la rete, ecc... vi sono alcune variabili di ambiente di cui è necessario specificare il significato:

- bootstrap.memory_lock=true => permette di disattivare lo swapping 

- "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m" => definisce il valore massimo e minimo della dimensione dell'heap Java

- 9600:9600 => questa porta viene aperta per l'uso del Performance Analyzer

Per far partire il cluster basterà eseguire

        docker-compose up

All'interno della cartella.


# 4. Mini-cluster
A causa dell'elevato numero di risorse richieste dal cluster a 4 nodi si è realizzato una versione leggera di quest'ultimo. Vi è un solo nodo opensearch, inoltre, sono stati disabilitati alcuni plugin che in un contesto locale non risultano molto utili, come il plugin sulla sicurezza. Difatti, nel docker-compose sono state aggiunte (oltre al servizio logstash) alcune nuove variabili d'ambiente, oltre a quelle viste prima:

- "DISABLE_INSTALL_DEMO_CONFIG=true" => permette di disabilitare l'esecuzione di install_demo_configuration.sh, solitamente legato al plugin sulla sicurezza; tale script installa i certificati della demo e le configurazioni di sicurezza su OpenSearch

- "DISABLE_SECURITY_PLUGIN=true" => disabilita il plugin sulla sicurezza

- "DISABLE_SECURITY_DASHBOARDS_PLUGIN=true" => disabilita il plugin della sicurezza sulla dashboard

Per il resto, la gestione del cluster è pressochè identica.

# 5. k8s-test
Come già trattato nella relazione, si è realizzato una semplice implementazione su Kubernetes del mini-cluster. Sono infatti presenti nella cartella i file .yml necessari. Una volta avviato Minikube

        minikube start

Basterà aggiungere i file tramite il comando 

        kubetctl apply -f <directory-with-.yml-files>

Dopodiché, per verificare lo stato del cluster, basterà usare kubectl

        kubectl get all

Oppure, servirsi dell'estensione per Kubernetes di vscode.


# 6. Configurazione di OpenSearch
Prima di iniziare a caricare i dati all'interno di OpenSearch è necessario andare a creare un indice apposito. Per tale motivo, dalla console OpenSearch è quindi necessario inserire i seguenti commandi.

    PUT tweetslog/_settings
    {
    "index.mapping.total_fields.limit": 1500
    }

Tale comando permette di gestire i tweet con un elevato numero di campi, contemporaneamente, verrà creato l'indice "tweetslog".
Dopodiché è necessario mappare gli attributi di interesse; opensearch non è infatto in grado di dedurre automaticamente che le coordinate geografiche sono geopoint, o individuare la data di creazione. 
Si usano quindi questi comandi

  
    PUT tweetslog
    {
      "mappings": {
        "properties": {
          "coordinates": {
            "type": "geo_point",
            "ignore_malformed" : true
          },
          "created_at" : {
            "type" : "date",
            "format" : "EEE MMM dd HH:mm:ss Z YYYY"
          }
        }
      }
    }



Ovviamente, come già descritto nella relazione, per visualizzare i dati sarà necessario creare un index pattern nella dashboard.









