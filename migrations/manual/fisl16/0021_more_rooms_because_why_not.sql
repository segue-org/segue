BEGIN TRANSACTION;

    INSERT INTO room (position, name, capacity, translation)
              VALUES (18, 'Sindicato Afocefe', 40, 'f');

    INSERT INTO slot (room_id, begins, duration, status)
              (SELECT id, '2015-07-09 09:00:00', 60, 'empty' FROM room WHERE name = 'Sindicato Afocefe');
COMMIT;
