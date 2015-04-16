BEGIN TRANSACTION;

    UPDATE caravan SET sold_until = '2015-04-26' WHERE category = 'caravan' AND price = 60;
    UPDATE caravan SET sold_until = '2015-05-10' WHERE category = 'caravan' AND price = 85;
    UPDATE caravan SET sold_until = '2015-05-18' WHERE category = 'caravan' AND price = 110;
    UPDATE caravan SET sold_until = '2015-06-15' WHERE category = 'caravan' AND price = 135;
    UPDATE caravan SET sold_until = '2015-06-30' WHERE category = 'caravan' AND price = 160;

COMMIT;

