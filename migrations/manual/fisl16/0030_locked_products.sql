BEGIN TRANSACTION;

INSERT INTO product (kind,     category,       can_pay_cash, gives_kit, "public", price, sold_until,            description)
             VALUES ('ticket', 'press',        'f',          'f',       'f',      0,     '2015-07-11 23:59:59', E'imprensa'),
                    ('ticket', 'support',      'f',          'f',       'f',      0,     '2015-07-11 23:59:59', E'suporte'),
                    ('ticket', 'service',      'f',          'f',       'f',      0,     '2015-07-11 23:59:59', E'servi\u00E7os'),
                    ('ticket', 'exhibitor',    'f',          'f',       'f',      0,     '2015-07-11 23:59:59', E'expositor'),
                    ('ticket', 'organization', 'f',          'f',       'f',      0,     '2015-07-11 23:59:59', E'organizador');


COMMIT;
