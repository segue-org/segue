BEGIN TRANSACTION;

INSERT INTO product (kind, category, can_pay_cash, "public", price, sold_until, description)
VALUES ('ticket', 'normal',  't', 't', 350, '2015-07-11 23:59:29', 'ingresso FISL16 - individual - lote 6'),
       ('ticket', 'student', 't', 't', 175, '2015-07-11 23:59:29', 'ingresso FISL16 - estudante - lote 6'),
       ('ticket', 'caravan', 't', 'f', 175, '2015-07-11 23:59:29', 'ingresso FISL16 - caravana - lote 6');

COMMIT;

