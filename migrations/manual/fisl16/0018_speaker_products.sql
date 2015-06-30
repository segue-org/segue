BEGIN TRANSACTION;

INSERT INTO product (kind, category, "public", price, sold_until, description)
VALUES ('ticket', 'speaker', 'f', 350, '2015-07-11 23:59:29', 'ingresso FISL16 - PALESTRANTE');

COMMIT;

