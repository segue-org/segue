BEGIN TRANSACTION;

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'proponent-student', 'F', 60,  '2015-04-13 23:59:59', 'ingresso FISL16 - proponente estudante - lote 1');

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'proponent-student', 'F', 85,  '2015-04-20 23:59:59', 'ingresso FISL16 - proponente estudante - lote 2');

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'proponent', 'F', 120,  '2015-04-13 23:59:59', 'ingresso FISL16 - proponente normal - lote 1');

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'proponent', 'F', 170,  '2015-04-20 23:59:59', 'ingresso FISL16 - proponente normal - lote 2');


COMMIT;

