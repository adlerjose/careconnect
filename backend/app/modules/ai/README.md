# Módulo de Inteligência Artificial — CareConnect PI

O módulo de Inteligência Artificial (`backend/app/modules/ai`) é o componente central responsável por interpretar relatos pós-atendimento de pacientes recebidos via WhatsApp (texto ou áudio) e transformá-los em estruturas de dados padronizadas (`ClinicalExtractionResult`) para subsidiar a triagem e o acompanhamento clínico por profissionais de saúde.

---

## 1. Princípios Éticos e Segurança Clínica

1. **Caráter Estritamente Auxiliar**: A IA atua unicamente como extratora e organizadora de dados de relatos não estruturados.
2. **Vedação de Diagnóstico e Prescrição**: O sistema é proibido de sugerir patologias, emitir diagnósticos definitivos, prescrever medicamentos ou indicar alterações de dosagens.
3. **Revisão Humana Obrigatória**: Toda extração clínica (seja de texto ou áudio) impõe obrigatoriamente `requires_human_review = True`, garantindo que nenhuma tomada de decisão ocorra sem a chancela de um profissional de saúde responsável.
4. **Privacidade e Proteção de Dados (LGPD/HIPAA)**:
   - Nenhum identificador (`patient_id`, `message_id`) é compartilhado com provedores de IA externos.
   - Bytes de áudio, dados de voz ou transcrições completas não são expostos em logs da aplicação.
   - Áudios são processados em memória volátil durante a requisição e descartados após o processamento.

---

## 2. Arquitetura do Processamento de Áudio

```
                                  +------------------------------------+
                                  |     Backend / Webhook Service      |
                                  |  (Valida origem, baixa o arquivo,  |
                                  |    gera bytes e MIME type seguro)  |
                                  +-----------------+------------------+
                                                    |
                                                    | (AIMessageInput com audio_bytes)
                                                    v
                                  +------------------------------------+
                                  |    ClinicalExtractionPipeline      |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |          GeminiProvider            |
                                  +-----------------+------------------+
                                                    |
                     +------------------------------+------------------------------+
                     | Validações de Segurança:                                    |
                     | 1. Proteção SSRF (rejeita URLs remotas diretas)             |
                     | 2. Validação de tamanho (máximo 20MB)                       |
                     | 3. Sniffing de magic bytes (OGG, MP3, WAV, M4A, AAC, FLAC)  |
                     +------------------------------+------------------------------+
                                                    |
                                                    | (Part.from_bytes + Prompt Clínico)
                                                    v
                                  +------------------------------------+
                                  |     Google Gemini API (SDK 1.x)    |
                                  |      (gemini-3.5-flash-lite)       |
                                  |    com Structured Outputs (JSON)   |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |      ClinicalExtractionResult      |
                                  |    (requires_human_review=True)    |
                                  +------------------------------------+
```

---

## 3. Formatos Suportados e Limites Técnicos

### Formatos de Áudio Aceitos
A inspeção utiliza **magic bytes** nos cabeçalhos binários e suporta os seguintes formatos:
- **OGG / Opus** (`audio/ogg`, `audio/opus`): formato padrão das mensagens de voz do WhatsApp.
- **MP3** (`audio/mp3`, `audio/mpeg`): cabeçalhos ID3v2 e frames MPEG sincronizados.
- **WAV** (`audio/wav`, `audio/x-wav`): contêiner RIFF/WAVE.
- **M4A / MP4** (`audio/m4a`, `audio/mp4`): contêineres QuickTime/MP4 com marca ftyp.
- **AAC** (`audio/aac`): fluxos de áudio ADTS.
- **FLAC** (`audio/flac`): áudio sem perdas (lossless).

### Limites Estabelecidos para o MVP
- **Tamanho Máximo por Arquivo**: `20 MB` (limite conservador para envio seguro inline multimodal).
- **Arquivos Vazios**: Rejeitados preventivamente com `AIExtractionError`.
- **Arquivos Corrompidos / Não-Áudio**: Bloqueio ativo se os bytes iniciais coincidirem com PDF, PNG, JPEG, ZIP, HTML ou JSON.

---

## 4. Contratos de Dados

### Entrada: `AIMessageInput`
```python
class AIMessageInput(BaseModel):
    message_id: str               # ID único da mensagem (não enviado à IA)
    patient_id: str               # ID único do paciente (não enviado à IA)
    message_type: MessageType     # TEXT ou AUDIO
    content: Optional[str]        # Preenchido quando TEXT
    audio_bytes: Optional[bytes]  # Bytes binários pré-carregados pelo backend
    mime_type: Optional[str]      # MIME type do áudio (ex: 'audio/ogg')
    audio_url: Optional[str]      # Referência de rastreabilidade interna ou caminho local
```

### Saída: `ClinicalExtractionResult`
```python
class ClinicalExtractionResult(BaseModel):
    symptoms: List[str]                  # Sintomas expressamente relatados
    duration: Optional[str]              # Duração informada (ex: '3 dias')
    medications: List[str]               # Medicamentos citados com dosagens
    clinical_summary: Optional[str]      # Resumo objetivo da fala ou limitação técnica
    confidence: Optional[float]          # Grau de certeza da extração clínica (0.0 a 1.0)
    requires_human_review: bool = True   # Obrigatoriamente True no MVP
```

#### Política de Calibração de Confiança (`confidence`):
- **Não é probabilidade médica**: O campo `confidence` indica estritamente a clareza da extração textual/multimodal, nunca uma garantia diagnóstica ou índice de gravidade clínica.
- **Áudios inaudíveis ou sem fala**: Se o áudio estiver vazio, mudo ou incompreensível por ruído, a aplicação calibra a confiança obrigatoriamente para `0.0`. Isso impede que o sistema apresente o paciente como "assintomático com 100% de certeza".
- **Áudios parcialmente compreensíveis**: Mantém pontuação intermediária (ex: 0.1 a 0.5) descrevendo as limitações no `clinical_summary`.
- **Salvaguarda mandatória**: `requires_human_review = True` é forçado incondicionalmente em todas as requisições.

---

## 5. Prevenção Contra SSRF (Server-Side Request Forgery)

O provedor `GeminiProvider` **NÃO realiza downloads diretos de URLs arbitrárias da Internet** (`http://` ou `https://`).

Essa decisão arquitetural elimina vulnerabilidades de requisições maliciosas contra serviços internos da rede ou vazamento de credenciais locais. É responsabilidade exclusiva da camada de mensageria/backend efetuar o download seguro do arquivo de áudio e injetar os bytes validados no contrato `audio_bytes`.

---

## 6. Como Executar os Testes

### 6.1. Testes Automatizados (Mocks — sem consumo de API)
Para rodar toda a suíte de testes do módulo de IA (64 testes cobrindo rotas felizes, formatos inválidos, timeouts, erros 503/429/401, safety blocks, calibração semântica de áudio inaudível e isolamento de logs):

```bash
cd backend
source .venv/bin/activate
pytest app/modules/ai/tests/ -v
```

### 6.2. Teste Manual com Áudio Real (Google Gemini)
Para executar uma chamada real contra a API do Google Gemini:

```bash
cd backend
source .venv/bin/activate

# 1. Teste rápido gerando áudio sintético em memória:
python scripts/manual_gemini_audio_test.py

# 2. Teste fornecendo um arquivo de áudio gravado (ex: OGG do WhatsApp ou WAV):
python scripts/manual_gemini_audio_test.py caminho/para/audio_relato.ogg
```

---

## 7. Limitações Conhecidas

1. **Dependência de Qualidade Sonora**: Áudios com ruído extremo de trânsito/vento, vozes sobrepostas ou fala sussurrada podem gerar resumos indicando incompreensão com confiança reduzida (o que aciona corretamente a salvaguarda de revisão humana).
2. **Envio Inline (limite de 20MB)**: Mensagens com duração superior a ~20 minutos podem exceder o limite de 20MB e necessitarão de upload prévio via Gemini Files API em etapas posteriores.
3. **Variações de Pronúncia Dialetal**: Embora o prompt esteja calibrado para o português brasileiro, termos coloquiais médicos regionais atípicos podem exigir confirmação na revisão humana.

---

## 8. Roteiro de Integração Futura com a Evolution API

> [!NOTE]
> A integração com a Evolution API e o recebimento de webhooks do WhatsApp **não fazem parte do escopo atual desta etapa** e serão implementados em módulo dedicado subsequente.

O fluxo futuro será:
1. **Webhook da Evolution API**: O backend recebe a notificação `messages.upsert` com uma mensagem de áudio (formato OGG/Opus).
2. **Download Seguro**: O backend utiliza os endpoints da Evolution API com autenticação e validação de tokens para baixar os bytes do áudio.
3. **Instanciação do Contrato**: O backend cria uma instância de `AIMessageInput(message_type=MessageType.AUDIO, audio_bytes=raw_bytes, mime_type="audio/ogg")`.
4. **Execução do Pipeline**: `ClinicalExtractionPipeline.run(message)` encaminha os dados ao provedor ativo.
5. **Persistência e Notificação**: O resultado estruturado é persistido no banco de dados relacional e encaminhado ao dashboard dos profissionais.
