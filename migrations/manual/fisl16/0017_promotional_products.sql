BEGIN TRANSACTION;

INSERT INTO product (kind, description, category, price, sold_until, gives_kit, is_promo, "public")
VALUES ('ticket', 'insc. promocional - expositor',        'normal', 350, '2015-07-11 23:59:59', 't', 't', 'f'),
       ('ticket', 'insc. promocional - patrocinador',     'normal', 350, '2015-07-11 23:59:59', 't', 't', 'f'),
       ('ticket', 'insc. promocional - cortesia com kit', 'normal', 350, '2015-07-11 23:59:59', 't', 't', 'f'),
       ('ticket', 'insc. promocional - cortesia sem kit', 'normal', 350, '2015-07-11 23:59:59', 'f', 't', 'f'),
       ('ticket', 'insc. promocional - comunidades',      'normal', 350, '2015-07-11 23:59:59', 't', 't', 'f'),
       ('ticket', 'insc. promocional - associados',       'normal', 350, '2015-07-11 23:59:59', 't', 't', 'f'),
       ('ticket', 'insc. promocional - especial',         'normal', 350, '2015-07-11 23:59:59', 't', 't', 'f');

COMMIT;
