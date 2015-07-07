BEGIN TRANSACTION;

INSERT INTO product (category, price, description, original_deadline)
VALUES
    ('foreigner', 120, 'ingresso FISL16 - estrangeiro - lote 1', '2015-04-13 23:59:59'),
    ('foreigner', 170, 'ingresso FISL16 - estrangeiro - lote 2', '2015-04-20 23:59:59'),
    ('foreigner', 220, 'ingresso FISL16 - estrangeiro - lote 3', '2015-05-18 23:59:59'),
    ('foreigner', 270, 'ingresso FISL16 - estrangeiro - lote 4', '2015-06-15 23:59:59'),
    ('foreigner', 320, 'ingresso FISL16 - estrangeiro - lote 5', '2015-06-30 23:59:59'),
    ('foreigner', 350, 'ingresso FISL16 - estrangeiro - lote 6', '2015-07-11 23:59:29'),

    ('foreigner-student',  60, 'ingresso FISL16 - estrangeiro estudante - lote 1', '2015-04-13 23:59:59'),
    ('foreigner-student',  85, 'ingresso FISL16 - estrangeiro estudante - lote 2', '2015-04-20 23:59:59'),
    ('foreigner-student', 110, 'ingresso FISL16 - estrangeiro estudante - lote 3', '2015-05-18 23:59:59'),
    ('foreigner-student', 135, 'ingresso FISL16 - estrangeiro estudante - lote 4', '2015-06-15 23:59:59'),
    ('foreigner-student', 160, 'ingresso FISL16 - estrangeiro estudante - lote 5', '2015-06-30 23:59:59'),
    ('foreigner-student', 175, 'ingresso FISL16 - estrangeiro estudante - lote 6', '2015-07-11 23:59:29');

UPDATE product SET kind         = 'ticket'              WHERE category LIKE 'foreigner%';
UPDATE product SET "public"     = 'f'                   WHERE category LIKE 'foreigner%';
UPDATE product SET sold_until   = '2015-07-11 23:59:59' WHERE category LIKE 'foreigner%';
UPDATE product SET can_pay_cash = 't'                   WHERE category LIKE 'foreigner%';

COMMIT;
