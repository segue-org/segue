BEGIN TRANSACTION;

INSERT INTO room (position, name, capacity, translation)
VALUES (1, '40T', 506, 'f'),
       (2, '41A', 351, 'f'),
       (3, '41B', 350, 'f'),
       (4, '41C', 250, 'f'),
       (5, '41D', 250, 'f'),
       (6, '41E', 250, 'f'),
       (7, '41F', 250, 'f'),
       (8, '40A', 110, 'f');

COMMIT;
