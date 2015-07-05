BEGIN TRANSACTION;

INSERT INTO product (kind, category, can_pay_cash, "public", price, sold_until, description)
VALUES ('ticket', 'caravan', 'f', 'f', 75, '2015-07-11 23:59:59', 'ingresso FISL16 - caravana - lote especial');

COMMIT;
