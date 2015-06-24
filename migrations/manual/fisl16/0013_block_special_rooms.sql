BEGIN TRANSACTION;

UPDATE slot SET blocked = 't' WHERE room_id IN (SELECT id FROM room where name = '40T');
UPDATE slot SET blocked = 't' WHERE room_id IN (SELECT id FROM room where name = '41A');
UPDATE slot SET blocked = 't' WHERE room_id IN (SELECT id FROM room where name = '41B');
UPDATE slot SET blocked = 't' WHERE room_id IN (SELECT id FROM room where name = 'Paulo Freire');
UPDATE slot SET blocked = 't' WHERE room_id IN (SELECT id FROM room where name = 'PMPA');
UPDATE slot SET blocked = 't' WHERE room_id IN (SELECT id FROM room where name = 'Lab. Tec. Livre');
UPDATE slot SET blocked = 't' WHERE room_id IN (SELECT id FROM room where name = 'Terr. Ap. Livre');
UPDATE slot SET blocked = 't' WHERE room_id IN (SELECT id FROM room where name = 'Hackaton Robot.');

COMMIT;
