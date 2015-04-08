BEGIN TRANSACTION;

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'caravan', 'F', 60,  '2015-04-13 23:59:59', 'ingresso FISL16 - caravana - lote 1');

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'caravan', 'F', 85,  '2015-04-20 23:59:59', 'ingresso FISL16 - caravana - lote 2');

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'caravan', 'F', 110, '2015-05-18 23:59:59', 'ingresso FISL16 - caravana - lote 3');

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'caravan', 'F', 135, '2015-06-15 23:59:59', 'ingresso FISL16 - caravana - lote 4');

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'caravan', 'F', 160, '2015-06-30 23:59:59', 'ingresso FISL16 - caravana - lote 5');

COMMIT;

