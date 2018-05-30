1) Verificar que ao utilizar pela primeira vez vai pegar todos clientes que
estão no Meus Pedidos e relacionar no sistema. Esse processo pode demorar
dependendo da quantidade de clientes que tem cadastrado.
    * Dica - Se não desejar relacionar todos clientes deve-se criar uma
    relação manual na tabela CLIENTES_MEUS_PEDIDOS informando a data limite.

2) Quanto aos pedidos já lançados deve ter atenção para somente relacionar os
novos pedidos. Para restringir, basta criar uma relação manual na tabela
PEDIDOS_MEUS_PEDIDOS, restringindo a data que se deseja integrar.


3) Lembrar de alterar o config.json de acordo com o exemplo
