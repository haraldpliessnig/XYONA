# Idee: XYONA Plugin Runtime und Rack

**Status:** Ideenskizze, keine Implementierungszusage  
**Datum:** 2026-05-01  
**Scope:** zukünftiges `xyona-plugin`, `xyona-core`, optional extrahierte
host-neutrale Runtime-Bausteine, Lab als Authoring-Host  
**Nicht-Scope:** `xyona-lab` als VST/AU einbetten

## Kurzentscheidung

XYONA als Plugin ist machbar, aber nur als eigenständiges DAW-taugliches
Runtime-Produkt. Es darf nicht die Lab-App im Host sein.

Das optimierte Zielbild ist:

```text
xyona-core
  Operatoren, DSP, Deskriptoren, Param-Semantik, Mapping, Preset-Migration
  keine JUCE-, Lab-, Device-, Canvas- oder DAW-Abhängigkeit

xyona-plugin-runtime
  JUCE-freie Plugin-Domain
  Rack-State, Host-Port-Modell, Parameter-Bindings, Macros, RT/HQ-Policy
  kompakte RT-Snapshots, State-Versionierung, Migration

xyona-plugin-juce
  JUCE AudioProcessor / AudioProcessorEditor
  VST3/AU, Host-Parameter, Host-State, Host-Transport, Plugin-UI

xyona-lab
  Standalone Authoring-Umgebung
  komplexe Patches, Presets, Operator-Design, Timeline/Grid, Export
```

Der wichtigste Architekturpunkt bleibt:

```text
stabile DAW Host-Ports
+ dynamische XYONA Operatoren
+ kompakte Binding-Snapshots
+ Macros als primäre Automation
+ versionierter semantischer State
```

## Produktmodell

Nicht bauen:

```text
"XYONA Lab als VST"
```

Das wäre zu schwer und host-unfreundlich:

- Canvas, Timeline, Device Settings, Projektverwaltung und große Lab-UI sind
  keine Plugin-Kernaufgaben.
- Lab ist HQ-first Authoring und Orchestration.
- DAW-Plugins müssen Session Recall, Automation, schnelle Instanzierung,
  deterministische Offline-Bounces und Host-Kompatibilität priorisieren.

Bauen:

```text
XYONA Rack
  dynamische Rack-Slots
  Operator-Browser
  Macros
  interne Modulation
  Preset-Browser
  DAW-stabile Host-Parameter
```

Optional später:

```text
XYONA Filter
XYONA Delay
XYONA Granular
XYONA Spectral FX
XYONA Dynamics
```

Diese Einzelplugins können denselben `xyona-plugin-runtime` nutzen, aber mit
festem Produkt-Scope und weniger Host-Ports.

## Begriffe, die nicht vermischt werden dürfen

Der bestehende XYONA-Slot-Vertrag und ein Plugin-Rack verwenden das Wort
"Slot" für unterschiedliche Dinge. Das muss im Code sauber getrennt werden.

| Begriff | Bedeutung |
|---|---|
| `RackSlot` | Ein Insert-Platz im Plugin-Rack, z. B. Slot 01 = Ladder Filter. |
| `OperatorSlot` | Die operator-interne Slot-Dimension aus `OPERATOR_CONTRACT.md`. |
| `HostPort` | Stabiler DAW-Parameter, z. B. `macro01` oder `rack03.param07`. |
| `ParameterBinding` | Nicht-RT Binding von HostPort/Macro zu Operator-Parameter. |
| `RtBindingSnapshot` | Kompakte, stringfreie Audio-Thread-Sicht. |
| `AudioChannel` | Audiokanal in einem Port, getrennt von RackSlot und OperatorSlot. |

Kanonische interne Zieladresse:

```text
rackSlotIndex
+ operatorInstanceId
+ operatorParamIndex
+ optional operatorSlotIndex
```

Kanonische Port-/Kabeladresse, falls das Rack später komplexere interne
Routings erhält:

```text
rackSlotIndex
+ descriptorPortId
+ optional channelIndex
+ optional operatorSlotIndex
```

## Plugin ohne Lab-AudioEngine

`xyona-plugin` sollte nicht `AudioEngineManager`, `AudioGraphBuilder`,
`GraphPlan`, Canvas, ProjectState oder Device-I/O aus Lab übernehmen.

Das Plugin braucht stattdessen eine kleinere Runtime:

```text
Plugin processBlock()
  Host buffer in/out
  Host transport snapshot
  Host automation port values
  published RuntimeSnapshot laden
  RackSlots in vorbereiteter Reihenfolge ausführen
  Parameter/Macro/Modulation block-stabil anwenden
  Output schreiben
```

Das ist eine DAW-Insert-Runtime, keine Lab-AudioEngine:

- keine Audio-Device-Verwaltung
- keine MainBus-/MonitoringSystem-Verantwortung
- keine Canvas-Graph-Interaktion im Audio-Thread
- keine Projektfenster, Expander, Timeline-Editoren
- keine Pack- oder Operator-Ladevorgänge im Audio-Thread

Interne Rack-Routings können später wachsen, sollten aber nicht mit der Lab
GraphPlan-Schicht starten.

## RT/HQ-Grundidee im Plugin

RT/HQ gehört auch ins Plugin, aber in kleinerer Form als in Lab.

### RT-Modus

Der normale DAW-Callback verwendet nur RT-fähige Operatoren:

```text
desc.caps.canRealtime == true
engine.materialization == none
wholeFileRequired == false
lengthChanging == false
```

Regeln:

- keine Heap-Allokation
- keine Locks
- keine String-Lookups
- keine Operator-/Pack-Ladevorgänge
- keine Topologieänderung
- keine Preset-Migration
- keine Descriptor-Parsing-Pfade

### HQ-/Offline-Modus

DAWs können Offline-Bounces fahren. Das Plugin darf dort eine bessere
Processing-Policy nutzen, aber nur unter einem strengen Vertrag:

```text
Host meldet non-realtime/offline
Operator kann HQ
Operator bleibt block-laengen-erhaltend
Operator braucht kein Whole-File-Material
RuntimeSnapshot ist vorbereitet
```

Dann darf gelten:

```text
RT playback:       processRealtime()
offline bounce:    processHQBlock() oder HQ policy
```

Nicht in V1:

- Whole-file CDP/HQ-Renderer direkt im DAW-Callback
- Hintergrund-HQ-Rendercache
- Lab-style MaterializedAudioStore im Plugin
- automatische RT/HQ Crossfades

Das kann später als eigenes Feature kommen:

```text
Plugin HQ Render Worker
  non-RT Background Thread
  vorbereitet aus Plugin-State
  Cache nur ausserhalb des Audio-Callbacks schreiben
  RT callback liest nur fertige, lockfreie Segmente
```

V1 sollte block-laengen-erhaltende RT/HQ-Operatoren sauber beherrschen, nicht
sofort das komplette Lab-HQ-Modell in ein Plugin ziehen.

## Host-Parameter-Modell

Host-Parameter müssen stabil bleiben. Operator-Parameter dürfen dynamisch sein.

Empfohlenes gestuftes Modell:

### Prototype

```text
16 Globals
16 Macros
0 technische RackSlot-Ports
= 32 Host-Parameter
```

Ziel: fester Core-Operator, DAW-Automation, State Restore, pluginval.

### Rack Lite

```text
16 Globals
32 Macros
4 RackSlots x 16 technische Ports
= 112 Host-Parameter
```

Ziel: dynamische Operatoren in wenigen RackSlots validieren.

### Rack V1

```text
16 Globals
64 Macros
8 RackSlots x 32 technische Ports
= 336 Host-Parameter
```

Das ist ein sinnvoller erster kommerzieller Rack-Umfang.

Nicht sofort:

```text
16 RackSlots x 64 Ports
1000+ Host-Parameter
4000+ Host-Parameter
```

Intern darf XYONA mehr Parameter verwalten. Die DAW sollte nur eine kontrollierte
Automationsoberflaeche sehen.

## HostPort-ID-Raum

Die numerische ID-Struktur soll grosszuegig reservieren, aber nicht alles
exportieren.

```cpp
static constexpr uint32_t kGlobalBase = 0x00000000;
static constexpr uint32_t kMacroBase  = 0x00010000;
static constexpr uint32_t kRackBase   = 0x00100000;
static constexpr uint32_t kModBase    = 0x01000000;
static constexpr uint32_t kFutureBase = 0x02000000;

uint32_t makeRackParamId(int rackSlotIndex, int paramIndex)
{
    return kRackBase
         + static_cast<uint32_t>(rackSlotIndex) * 0x1000
         + static_cast<uint32_t>(paramIndex);
}
```

Regeln:

- HostParamID nie semantisch brechen.
- Host-Parameteranzahl konservativ halten.
- Alle Host-Werte nach aussen `0.0..1.0`.
- Semantik lebt in XYONA, nicht in der DAW.
- Host-Metadaten sind Komfort, nicht State-Wahrheit.

## Macros als primäre DAW-Automation

DAW-User sollten vor allem Macros automatisieren.

```text
Macro 01 "Brightness"
  -> RackSlot 01 / cutoff
  -> RackSlot 03 / exciter_amount

Macro 02 "Space"
  -> RackSlot 02 / decay
  -> RackSlot 02 / damping
```

Vorteile:

- stabile Automation
- bessere DAW-UX
- controller-freundlich
- preset-freundlich
- weniger Chaos in Automation-Lanes

Technische RackSlot-Ports bleiben fuer Power-User verfuegbar, sollten aber
nicht das normale Bedienmodell sein.

## Binding- und Snapshot-Modell

Nicht-RT-Struktur:

```cpp
struct HostAutomationPort
{
    uint32_t stableHostParamId;
    std::string stableHostId; // "macro01", "rack03.param07"
    float value01;
};

struct ParameterBinding
{
    bool active;
    uint16_t rackSlotIndex;
    std::string operatorInstanceId;
    std::string operatorTypeId;
    std::string operatorParamId;
    std::optional<int> operatorSlotIndex;
    ParamKind kind;
    MappingCurve curve;
    double minValue;
    double maxValue;
    double defaultValue;
    std::string displayName;
    std::string unit;
};
```

RT-Struktur:

```cpp
struct RtPortBinding
{
    uint8_t active;
    uint16_t rackSlotIndex;
    uint16_t operatorParamIndex;
    int16_t operatorSlotIndex; // -1 = global
    MappingKind mappingKind;
    float minValue;
    float maxValue;
    float shape;
    uint16_t smoothingIndex;
};
```

Audio-Thread:

```cpp
for (const auto& port : snapshot.automatedPorts)
{
    const float v01 = port.value01.load(std::memory_order_relaxed);
    const auto& binding = snapshot.rtBindings[port.index];

    if (!binding.active)
        continue;

    const float plainValue = map01ToPlain(v01, binding);
    runtime.setParameter(binding, plainValue);
}
```

Der Audio-Thread bekommt nur vorbereitete Indizes und Werte. Keine Strings,
keine Maps, keine Descriptor-Suche.

## State-Modell

Plugin-State darf nicht nur Host-Werte speichern.

Er muss semantisch sein:

```json
{
  "schema": "xyona-plugin-rack-v1",
  "version": 1,
  "hostPorts": [
    { "id": "macro01", "value01": 0.73 }
  ],
  "rackSlots": [
    {
      "slot": 1,
      "operatorType": "xyona.filter.ladder",
      "operatorVersion": "3.0.0",
      "operatorInstanceId": "rack01.op01",
      "operatorSlotCount": 1,
      "params": [
        {
          "id": "cutoff",
          "value01": 0.736,
          "plainValue": 3240.0,
          "mapping": "log"
        }
      ],
      "hostBindings": [
        {
          "hostPort": "rack01.param01",
          "operatorParam": "cutoff",
          "operatorSlot": null,
          "policy": "port_automation"
        }
      ]
    }
  ],
  "macros": [
    {
      "macro": 1,
      "name": "Brightness",
      "targets": [
        {
          "rackSlot": 1,
          "operatorParam": "cutoff",
          "amount": 1.0,
          "curve": "linear"
        }
      ]
    }
  ],
  "missingTargets": []
}
```

Der JUCE Wrapper speichert diesen State als opaque Versioned Blob im Host.
JUCE `ValueTree` oder APVTS duerfen Transportformat sein, aber nicht die
Domain-Wahrheit.

## Kritik am aktuellen Parameter-System

### Stärken

Der aktuelle Stand hat starke Grundlagen:

- Core bleibt JUCE-frei.
- `OpDesc` und `ParamDesc` sind bereits die richtige Descriptor-Wahrheit.
- Lab hat `ParamAddress` inklusive optionalem Slot-Index.
- Lab hat eine lockfreie `ParameterUpdateQueue`.
- Lab nutzt stabile 64-bit `ParamKey` fuer RT-Updates.
- Lab hat block-stabile `ParameterSnapshot`s fuer Audio-Adapter.
- Timeline-Automation, Macro-Lanes, Modulation-Routen und
  `ParameterControlHub` existieren als Produktbausteine.
- Topologieparameter sind bekannt und koennen vom normalen RT-Wertepfad
  getrennt werden.

Das ist eine gute Basis. Es ist aber noch kein sauber vereinheitlichter
Plugin-Parametervertrag.

### Schwächen

1. **Normalisierung ist nicht kanonisch genug.**  
   Core `Parameter::setNormalized()` ist float-only und linear. Die vorhandene
   Scaling-Information ist nicht als vollstaendiger, getesteter
   Descriptor-Codec verfuegbar. Ein Plugin braucht fuer jeden ParamKind eine
   eindeutige `0..1 <-> plain value` Abbildung.

2. **Mapping/Smoothing sind nicht ausreichend Vertrag.**  
   `ParamDesc` hat Typ, Min/Max, Default, Unit und Display-Hints, aber noch
   keine robuste gemeinsame MappingCurve-, Step-, Formatter-, Parser- und
   Smoothing-Policy als harte Semantik.

3. **Es gibt mehrere Parameter-Wahrheiten.**  
   Lab hat Canvas `paramValues`, `ParameterRegistry`, `ParameterControlHub`,
   Timeline-Lanes, AudioSnapshots und Core-Operator-Parameter. Das ist fuer Lab
   historisch erklaerbar, aber fuer ein Plugin zu riskant, wenn keine gemeinsame
   semantische Schicht darunter liegt.

4. **Core `ParameterSnapshot` ist nicht RT-ideal.**  
   Die Core-Struktur verwendet `unordered_map<string, variant>`. Lab hat eine
   effizientere Runtime-Snapshot-Struktur, aber die ist Lab-spezifisch. Das ist
   ein klares Zeichen, dass ein host-neutraler RT-Parameterblock fehlt.

5. **String-basierte Per-Slot-Keys sind nur als Persistence-Bruecke gut.**  
   `gain@slot=N` ist lesbar und fuer Migration praktisch. Im Audio-Thread muss
   daraus aber ein vorbereiteter Index werden.

6. **Automation und Modulation sind produktseitig reich, aber nicht DAW-konform
   genug abstrahiert.**  
   Lab-Automation ist Timeline-/Projekt-orientiert. Plugin-Automation ist
   HostPort-/Session-orientiert. Beides darf dieselbe Wertsemantik nutzen, aber
   nicht dieselbe Host-Policy erzwingen.

7. **Topologieparameter brauchen eine haertere Sperre.**  
   Im Audio-Adapter werden Topologieparameter bereits ausgespart. Fuer ein
   Plugin muss das Vertragsregel werden: Topologieaenderungen sind Commands auf
   Message/Worker Thread, niemals normale Audio-Thread-Parameterwrites.

8. **Parameterzugriff ist teilweise linear/lookup-lastig.**  
   Fuer ein Rack mit vielen Ports und vielen Instanzen braucht es kompilierte
   Param-Indizes pro Operatorinstanz, nicht wiederholtes Suchen ueber
   Bindings/Hashes.

## Kritik am aktuellen Automation-System

### Stärken

- Lab hat Timeline-Automation, Macro-Lanes und Modulation-Lanes als getrennte
  Produktkonzepte.
- `ParameterControlHub` trennt Manual, Automation und Modulation als Quellen.
- Es gibt vorbereitete Runtime-Strukturen fuer Modulation und Signal-Sources.
- Block-stabile Parametermodulation ist explizit dokumentiert; sample-genaue
  Modulation soll ueber Signal/CV laufen.

### Schwächen fuer das Plugin

1. **DAW-Automation braucht stabile externe Ports.**  
   Lab-Automation adressiert `NodeId + ParamId`. Plugin-Automation muss
   `HostPortId` adressieren und darf nie von dynamischem Operatorwechsel
   abhaengen.

2. **Host-Automation ist nicht Timeline-Automation.**  
   DAW-Automation kommt ueber Plugin-Parameterwerte, manchmal mit
   sample offsets, manchmal blockweise, host-spezifisch. Lab-Timeline-Lanes
   koennen diese Rolle nicht direkt uebernehmen.

3. **Macro-Semantik muss erster Klasse werden.**  
   Macros duerfen nicht nur UI-Komfort sein. Im Plugin sind sie die wichtigste
   Automationsebene und muessen eigene State-, Naming-, Mapping-, Smoothing- und
   Missing-Target-Regeln haben.

4. **Automation-Policy bei Operatorwechsel fehlt als harter Vertrag.**  
   "Port bleibt aktiv" ist fuer V1 moeglich, aber riskant. Langfristig braucht
   es Target-Lock und Missing-Target-State.

5. **Automation-Werte brauchen klare Normalisierungsdomäne.**  
   DAW-Host-Werte sind `0..1`. Interne XYONA-Werte koennen Hz, dB, Sekunden,
   Enum-Indizes oder bool sein. Die Konvertierung muss zentral und versioniert
   sein.

## Vereinheitlichen oder getrennt lassen?

Antwort: Semantik vereinheitlichen, Hosts getrennt lassen.

Vereinheitlichen:

- `ParamKind`
- `MappingCurve`
- `ParamValueCodec`
- `SmoothingPolicy`
- `NormalisedValue01`
- `PlainParamValue`
- versionierter Param-/Preset-State
- Missing-Target-Modell
- kompakte RT-Parameterblocks
- Descriptor-Validierung fuer Automatisierbarkeit

Nicht vereinheitlichen:

- Lab ParameterCenter UI
- Lab Timeline-Automation UX
- Lab ProjectState/Undo/Redo
- Lab AudioEngineManager/GraphPlan
- Plugin HostParam-Export
- Plugin `AudioProcessor` State-Callbacks
- DAW-spezifische Automation-Gesten und Host-Metadaten

Das heisst:

```text
Core/shared runtime:
  Was bedeutet dieser Parameter?
  Wie wird 0..1 gemappt?
  Wie wird geglaettet?
  Wie wird State migriert?
  Wie sieht ein RT-sicherer Paramblock aus?

Lab:
  Wie authored, visualisiert, automatisiert und speichert die Standalone-App?

Plugin:
  Wie wird derselbe semantische Zustand DAW-stabil auf Host-Ports projiziert?
```

Ein gemeinsames `xyona-runtime` oder `xyona-param-runtime` kann sinnvoll sein,
wenn es strikt JUCE-frei bleibt und weder Lab- noch DAW-Begriffe kennt.

## Automation-Merge im Plugin

Empfohlene Reihenfolge:

```text
1. Preset/default state
2. DAW HostPort values
3. Macro evaluation
4. internal modulation
5. smoothing
6. final plain parameter write
```

Wichtig:

- DAW HostPort-Werte sind externe Automationsquellen.
- Macros koennen mehrere Targets schreiben.
- Interne Modulation darf nie HostPortIDs mutieren.
- Der Audio-Thread schreibt nur in vorbereitete Zielindizes.
- Macro-/Binding-Topologie wird per Snapshot atomar getauscht.

## Operatorwechsel-Policy

V1:

```text
Port Automation
  rack03.param07 steuert immer das aktuell gebundene Ziel.
```

Nur akzeptabel mit klarer Plugin-UI-Anzeige.

V2:

```text
Target Lock optional
  Binding gilt nur, wenn operatorType + paramId weiter passen.
```

V3:

```text
Missing Targets
  alte Automation bleibt semantisch sichtbar und kann neu gebunden werden.
```

Fuer professionelle Presets sollte V3 nicht zu lange verschoben werden.

## Pack-Loading im Plugin

Core hat bereits dynamisches Pack-Loading. Das Plugin sollte es nutzen, aber
Release-sicher:

Development:

```text
XYONA_OPERATOR_PACK_PATH
```

Produkt:

```text
Plugin bundle
  Contents/Resources/operator_packs/
  signierte und kompatibilitaetsgepruefte Packs
```

Risiken:

- macOS Hardened Runtime / Notarization
- Windows DLL search paths
- Pack ABI Versionen
- doppelte Pack-IDs
- Host-Crash-Risiko durch fehlerhafte Drittanbieter-Packs

Fuer V1 sollten nur eigene gebundelte Packs geladen werden. Drittanbieter-Packs
sind ein spaeteres Produkt- und Sicherheitsfeature.

## Phasenplan

### Phase 0 - Core/Runtime Vertrag

Ziel:

- ParamValueCodec
- MappingCurve
- SmoothingPolicy
- NormalisedValue01
- PlainParamValue
- RT-Parameterblock
- versionierter Plugin/Rack-State

DoD:

- Lab und Plugin koennen dieselbe Normalisierung verwenden.
- Keine string-/map-basierten Param-Lookups im geplanten Plugin-Audio-Thread.
- Topologieparameter sind vom normalen Automation-Pfad getrennt.

### Phase 1 - Fixed Operator Plugin

Ziel:

- ein JUCE VST3/AU mit festem Core-Operator
- 16 Globals + 16 Macros
- kein dynamisches Rack

DoD:

- pluginval sauber
- Ableton/Reaper/Logic laden das Plugin
- Host-Automation funktioniert
- State Save/Load klingt identisch
- Offline Bounce deterministisch
- processBlock allocation-free

### Phase 2 - Rack Lite

Ziel:

- 4 RackSlots
- 32 Macros
- 4 x 16 technische RackSlot-Ports
- dynamischer Operatorwechsel ausserhalb des Audio-Threads

DoD:

- Binding-Snapshot atomar publiziert
- Operatorwechsel ohne Audio-Thread-Mutation
- State Restore mit Operatorinstanzen und Parametern
- klare Policy fuer alte Automation

### Phase 3 - Rack V1

Ziel:

- 8 RackSlots
- 64 Macros
- 8 x 32 technische RackSlot-Ports
- 336 Host-Parameter

DoD:

- Macros sind Hauptautomation
- technische Ports funktionieren fuer Power-User
- Host-Metadaten best-effort
- UI zeigt echte Operatorsemantik

### Phase 4 - Lab Preset Export

Ziel:

- Lab authored Rack-Presets
- Plugin laedt sie DAW-tauglich

Regel:

- Lab exportiert semantischen Rack-State.
- Plugin importiert und migriert.
- Plugin uebernimmt keine Lab-Projekt- oder Canvas-State-Strukturen.

### Phase 5 - Missing Targets und Migration

Ziel:

- robuste Presets bei Operatorwechsel
- Rebind UI
- Target-Lock
- Missing-Target-Inspektor
- Migration alter Plugin-States

## Haupt-Risiken

| Risiko | Bewertung | Gegenmassnahme |
|---|---:|---|
| Host-Parameter zu frueh zu gross | hoch | Prototype 32, Rack Lite 112, erst dann 336. |
| String-/Map-Lookups im Audio-Thread | hoch | RT-Parameterblock und kompilierte Bindings vor Rack V1. |
| OperatorSlot vs RackSlot verwechselt | hoch | getrennte Typen und Namen im Code. |
| Host-Metadaten als Wahrheit behandelt | hoch | Host-Metadata nur best-effort, Plugin-UI autoritativ. |
| Lab-AudioEngine versehentlich ins Plugin gezogen | hoch | `xyona-plugin-runtime` ohne Lab-Abhaengigkeit. |
| DAW-Automation steuert nach Operatorwechsel falsche Semantik | mittel/hoch | V1 UI-Warnung, V2 Target-Lock, V3 Missing Targets. |
| Pack-Signing/Distribution | mittel/hoch | V1 nur gebundelte signierte Packs. |
| RT/HQ-Vertrag zu breit | mittel | V1 nur block-laengen-erhaltende RT/HQ-Operatoren. |

## Empfehlung

Nicht direkt das grosse Rack bauen.

Der naechste sinnvolle Architektur-Meilenstein ist:

```text
Host-neutraler Parameter-/Automation-Kern
+ Fixed Operator Plugin Prototype
```

Erst wenn diese beiden Dinge hart validiert sind, sollte das dynamische Rack
kommen.

Die entscheidende Linie:

```text
XYONA Lab bleibt Authoring und HQ-first Standalone.
XYONA Plugin wird DAW-first Runtime.
Beide teilen Parametersemantik, Deskriptoren, Mapping, Migration und Core-DSP.
Sie teilen nicht dieselbe UI-, Projekt-, Device- oder AudioEngine-Schicht.
```

