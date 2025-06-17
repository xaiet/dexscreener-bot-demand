# Bot de detecció de tokens en tendència

Aquest projecte és un **bot de Telegram** connectat a **Solana** i a la plataforma **Birdeye**, dissenyat per detectar automàticament tokens nous amb potencial de creixement.

## Funcionalitats

- Comandes interactives:
  - `/tendencia`: mostra tokens amb indicadors de creixement en les darreres hores
  - `/status`: comprova que el bot està actiu
  - `/id`: mostra el teu `chat_id` per configurar alertes

- Notificacions automàtiques cada 4 hores si es detecten tokens amb potencial
- Filtres de seguretat per evitar tokens sospitosos o amb distribució de holders perillosa
- Verificació que els tokens es poden comprar via **Jupiter** (Solana DEX aggregator)

## Requisits

- Python 3.8+
- Token d'accés per a un bot de Telegram
- Clau d'API de **Birdeye**

## Avís

Aquest projecte és experimental i **no s'ha de considerar assessorament financer**. Utilitza'l sota la teva responsabilitat.
