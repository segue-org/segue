BEGIN TRANSACTION;

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'corporate', 'F', 120,  '2015-04-20 23:59:59', 'ingresso FISL16 - corporativo - lote 1');

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'corporate', 'F', 170,  '2015-04-11 23:59:59', 'ingresso FISL16 - corporativo - lote 2');

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'corporate', 'F', 220, '2015-05-18 23:59:59', 'ingresso FISL16 - corporativo - lote 3');

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'corporate', 'F', 270, '2015-06-15 23:59:59', 'ingresso FISL16 - corporativo - lote 4');

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'corporate', 'F', 320, '2015-06-30 23:59:59', 'ingresso FISL16 - corporativo - lote 5');

COMMIT;

