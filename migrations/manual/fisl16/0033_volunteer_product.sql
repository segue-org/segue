BEGIN TRANSACTION;

INSERT INTO product (kind,     category,       can_pay_cash, gives_kit, "public", price, sold_until,            description)
             VALUES ('ticket', 'volunteer',    'f',          'f',       'f',      0,     '2015-07-11 23:59:59', E'volunt\u00E1rios');


COMMIT;
