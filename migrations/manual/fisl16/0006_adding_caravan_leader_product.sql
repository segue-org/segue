BEGIN TRANSACTION;

    INSERT INTO PRODUCT (kind, category, "public", price, sold_until, description)
                 VALUES ('ticket', 'caravan-leader', 'F', 0,  '2015-06-30 23:59:59', 'ingresso FISL16 - lider caravana - cortesia');

COMMIT;
