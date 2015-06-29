BEGIN TRANSACTION;

    INSERT INTO product (kind, category, "public", price, original_deadline, description)
                 VALUES ('ticket', 'proponent-student', 'F', 60,  '2015-04-13 23:59:59', 'ingresso FISL16 - proponente estudante - lote 1');

    INSERT INTO product (kind, category, "public", price, original_deadline, description)
                 VALUES ('ticket', 'proponent-student', 'F', 85,  '2015-04-20 23:59:59', 'ingresso FISL16 - proponente estudante - lote 2');

    INSERT INTO product (kind, category, "public", price, original_deadline, description)
                 VALUES ('ticket', 'proponent', 'F', 120,  '2015-04-13 23:59:59', 'ingresso FISL16 - proponente normal - lote 1');

    INSERT INTO product (kind, category, "public", price, original_deadline, description)
                 VALUES ('ticket', 'proponent', 'F', 170,  '2015-04-20 23:59:59', 'ingresso FISL16 - proponente normal - lote 2');

    UPDATE product SET sold_until = '2015-06-30 23:59:59' WHERE category = 'proponent';
    UPDATE product SET sold_until = '2015-06-30 23:59:59' WHERE category = 'proponent-student';

COMMIT;

