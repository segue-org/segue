BEGIN TRANSACTION;

INSERT INTO product (kind, category, can_pay_cash, "public", price, sold_until, description)
VALUES ('ticket', 'empenho', 'f', 'f', 350, '2015-07-11 23:59:59', 'insc. por empenho - lote unico');

COMMIT;
