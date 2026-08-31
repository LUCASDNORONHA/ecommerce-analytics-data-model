/*
Objetivo: formar a base de pagamentos sem multiplicar sequências.
Pergunta: qual valor foi registrado e como o pagamento se compõe por pedido?
Entrada: core.pagamento, uma linha por sequência de pagamento.
Saída: uma linha por id_pedido.
Data de referência: não incluída; combinar com core.pedido após esta agregação.
Filtros: pedidos que possuem pagamentos.
Limitação: valor registrado não comprova liquidação, estorno ou receita.
*/

SELECT
    id_pedido,
    COUNT(*) AS quantidade_registros_pagamento,
    COUNT(DISTINCT tipo_pagamento) AS quantidade_tipos_pagamento,
    SUM(valor_pagamento) AS valor_pago_registrado,
    MAX(numero_parcelas) AS maior_numero_parcelas,
    STRING_AGG(
        DISTINCT tipo_pagamento,
        ', ' ORDER BY tipo_pagamento
    ) AS tipos_pagamento
FROM core.pagamento
GROUP BY id_pedido
ORDER BY id_pedido;
