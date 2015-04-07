BEGIN TRANSACTION;

    UPDATE product SET sold_until = '2015-04-13 23:59:59' WHERE sold_until = '2015-04-06 23:59:59';

COMMIT;

