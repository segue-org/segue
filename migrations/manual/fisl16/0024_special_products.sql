BEGIN TRANSACTION;

INSERT INTO product (kind, category, can_pay_cash, "public", price, sold_until, description)
VALUES ('ticket', 'government', 'f', 'f', 350, '2015-07-11 23:59:59', 'insc. por empenho - lote unico');

INSERT INTO product (kind, category, can_pay_cash, "public", price, sold_until, description)
VALUES ('ticket', 'business', 'f', 'f', 120, '2015-03-30 23:59:59', 'ingresso FISL16 - corporativo - lote 1');
INSERT INTO product (kind, category, can_pay_cash, "public", price, sold_until, description)
VALUES ('ticket', 'business', 'f', 'f', 170, '2015-04-13 23:59:59', 'ingresso FISL16 - corporativo - lote 2');
INSERT INTO product (kind, category, can_pay_cash, "public", price, sold_until, description)
VALUES ('ticket', 'business', 'f', 'f', 220, '2015-05-11 23:59:59', 'ingresso FISL16 - corporativo - lote 3');
INSERT INTO product (kind, category, can_pay_cash, "public", price, sold_until, description)
VALUES ('ticket', 'business', 'f', 'f', 270, '2015-06-11 23:59:59', 'ingresso FISL16 - corporativo - lote 4');
INSERT INTO product (kind, category, can_pay_cash, "public", price, sold_until, description)
VALUES ('ticket', 'business', 'f', 'f', 320, '2015-06-30 23:59:59', 'ingresso FISL16 - corporativo - lote 5');
INSERT INTO product (kind, category, can_pay_cash, "public", price, sold_until, description)
VALUES ('ticket', 'business', 'f', 'f', 350, '2015-07-11 23:59:59', 'ingresso FISL16 - corporativo - lote 6');

COMMIT;
