# Philips 2 — Ponte Android para Philips 50PUG6654/78

Este módulo é a camada Android nativa necessária para transmitir infravermelho. O site/PWA hospedado no Lovable não tem acesso direto ao emissor IR do Android.

## Estado de compatibilidade
- Modelo-alvo: Philips 50PUG6654/78 (série 6600, plataforma SAPHI). IP informado: 192.168.1.2. A TV possui Wi-Fi 802.11n e Ethernet RJ-45; a API de rede SAPHI deve ser testada com a TV ligada. O manual oficial confirma Wake-on-WLAN em standby. Ative na TV: Início > Definições > Todas as configurações > Sem fio e redes > Ligar com Wi-Fi (WoWLAN) > Ligado. O envio do pacote mágico também exige o MAC da TV; o app tenta descobri-lo na rede ao sincronizar com a TV ligada.
- Hardware IR: detectado em tempo de execução por `ConsumerIrManager`.
- Perfil IR: **não configurado**. Não inserir códigos presumidos.
- RC5/RC6: não assumir sem confirmação específica do modelo/controle.

## Integração
A Activity expõe `window.PhilipsIR` ao WebView. A página pode consultar `getStatus()` e solicitar `send(command)`. A transmissão só ocorre quando houver um código de pulsos validado cadastrado no perfil JSON. O retorno confirma apenas que o Android transmitiu o sinal, não que a TV o recebeu.

## Compilar
Abra a pasta `android` no Android Studio e compile o módulo `app`. O dispositivo precisa ter emissor IR e API Android compatível. A versão web deste repositório continua disponível em https://philips-2.lovable.app.

## Próximo requisito para ativar comandos
Os códigos IR continuam vazios até serem medidos ou confirmados para o controle original da 50PUG6654/78. Não reutilizar códigos de outros modelos.
