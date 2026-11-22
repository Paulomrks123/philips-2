# Philips Pocket Zapper — Android IR bridge

Este módulo é a camada Android nativa necessária para transmitir infravermelho. O site/PWA hospedado no Lovable não tem acesso direto ao emissor IR do Android.

## Estado de compatibilidade
- Modelo-alvo documentado: Philips 26PFL3404 (controle PF01L09B).
- Hardware IR: detectado em tempo de execução por `ConsumerIrManager`.
- Perfil IR: **não configurado**. Não inserir códigos presumidos.
- RC5/RC6: não assumir sem confirmação específica do modelo/controle.

## Integração
A Activity expõe `window.PhilipsIR` ao WebView. A página pode consultar `getStatus()` e solicitar `send(command)`. A transmissão só ocorre quando houver um código de pulsos validado cadastrado no perfil JSON. O retorno confirma apenas que o Android transmitiu o sinal, não que a TV o recebeu.

## Compilar
Abra a pasta `android` no Android Studio e compile o módulo `app`. O dispositivo precisa ter emissor IR e API Android compatível. A versão web continua disponível em https://philips-pocket-zapper.lovable.app.

## Próximo requisito para ativar comandos
Obter uma tabela de códigos específica do Philips 26PFL3404/PF01L09B ou capturar os sinais de um controle compatível com receptor IR. Não usar códigos de modelos parecidos como substitutos.
