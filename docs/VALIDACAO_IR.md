# Auditoria técnica — Philips 26PFL3404

## O que foi confirmado

A página oficial de suporte Philips para o modelo **26PFL3404/78** identifica o tipo de controle remoto como **PF01L09B**. A documentação do produto confirma funções como Power, Menu, Source, navegação, OK, volume, canais, numérico, Info, Picture e Sound.

Fontes:
- [Suporte oficial Philips 26PFL3404/78](https://www.philips.com.br/c-p/26PFL3404_78/66-cm-26-polegada-hd-ready/suporte)
- [Manual do usuário Philips 26PFL3404/78](https://www.documents.philips.com/assets/20230308/16ea1207df744bf890cfafbf0078b92f.pdf)
- [Ficha técnica Philips 26PFL3404/78](https://www.documents.philips.com/assets/20230307/3083e691aebe4815a497afbe00ece35d.pdf)

A identificação PF01L09B é uma referência útil para procurar ou capturar sinais do controle original, mas **não é uma tabela de códigos IR**. Não prova, por si só, frequência, protocolo, endereço ou códigos de cada tecla.

## O que foi implementado no repositório

- PWA visual mantida separada do aplicativo Android nativo.
- Projeto Android gerado por `scripts/export_android.py`, usando Kotlin, Jetpack Compose e `ConsumerIrManager`.
- Diagnóstico de hardware e faixa de frequência IR.
- Bloqueio de comandos sem código comprovado para o modelo.
- Proteções contra padrões inválidos, frequência incompatível, chamadas rápidas e falhas de transmissão.
- Testes unitários do núcleo IR com backend falso.
- Workflow GitHub Actions para gerar o projeto Android, executar testes e compilar um APK de depuração como artefato.

## Limitações que ainda impedem declarar o controle funcional

1. Nenhum código de tecla foi confirmado especificamente para o 26PFL3404/PF01L09B. O perfil permanece intencionalmente vazio.
2. A PWA em navegador não consegue usar `ConsumerIrManager`; precisa do aplicativo Android nativo e de um emissor IR compatível.
3. A detecção do Android não comprova que a luz IR foi emitida corretamente nem que a TV recebeu o comando.
4. A confirmação final exige testar cada comando na TV física, com um celular que tenha emissor IR ou hardware externo realmente compatível.

## Próximos passos para concluir o perfil

- Confirmar a etiqueta completa da TV (por exemplo, 26PFL3404/78) e o controle original PF01L09B.
- Capturar cada tecla do controle original com receptor IR apropriado ou obter uma base de sinais que documente exatamente esse controle/modelo.
- Registrar portadora, tempos ON/OFF, protocolo e evidência da captura.
- Inserir apenas comandos validados em `PhilipsProfile.signals`.
- Compilar o APK, instalar em Android com emissor IR e testar cada tecla na TV.

**Não usar códigos genéricos Philips, códigos de outros modelos ou frequências presumidas como se fossem confirmados.**
