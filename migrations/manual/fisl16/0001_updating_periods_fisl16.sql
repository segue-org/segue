BEGIN TRANSACTION;

    UPDATE product SET sold_until = '2015-04-06 23:59:59' WHERE sold_until = '2015-03-30 23:59:59';
    UPDATE product SET sold_until = '2015-04-20 23:59:59' WHERE sold_until = '2015-04-13 23:59:59';
    UPDATE product SET sold_until = '2015-05-18 23:59:59' WHERE sold_until = '2015-05-11 23:59:59';
    UPDATE product SET sold_until = '2015-06-15 23:59:59' WHERE sold_until = '2015-06-08 23:59:59';
    UPDATE product SET sold_until = '2015-06-30 23:59:59' WHERE sold_until = '2015-06-30 23:59:59';

COMMIT;

