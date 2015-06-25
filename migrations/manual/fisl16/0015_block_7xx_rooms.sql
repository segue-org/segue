BEGIN TRANSACTION;

UPDATE slot SET blocked = 't' WHERE room_id IN (SELECT id FROM room where name like '712%');
UPDATE slot SET blocked = 't' WHERE room_id IN (SELECT id FROM room where name like '713%');
UPDATE slot SET blocked = 't' WHERE room_id IN (SELECT id FROM room where name like '714%');
UPDATE slot SET blocked = 't' WHERE room_id IN (SELECT id FROM room where name like '715%');

COMMIT;
