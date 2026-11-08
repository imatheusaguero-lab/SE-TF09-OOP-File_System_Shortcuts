# TF09 — Os 3 Pilares da Orientação a Objetos

- **Encapsulamento:** a classe `Atalho` disponibiliza a propriedade `destino` para consulta e o método `redirecionar()` para alteração, mantendo o atributo `__destino` protegido e suas validações internas.
- **Herança:** `Atalho` reutiliza a interface e a implementação de `Item`, herdando funcionalidades como `nome`, `pai`, `caminho()` e `mover_para()`, sem duplicar código.
- **Polimorfismo:** o método `tamanho()` possui a mesma interface nas diferentes classes, mas cada uma implementa seu próprio cálculo; no `Atalho`, o retorno é sempre 1 byte.
- **Interface `Medivel`:** define o contrato `tamanho()` sem implementar o cálculo, permitindo que `espaco_total()` utilize objetos diferentes sem conhecer seus detalhes internos.