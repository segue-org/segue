BEGIN TRANSACTION;

INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-08 09:00:00', 'empty', 60 from room where name = 'Paulo Freire');
INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-09 09:00:00', 'empty', 60 from room where name = 'Paulo Freire');
INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-10 09:00:00', 'empty', 60 from room where name = 'Paulo Freire');
INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-11 09:00:00', 'empty', 60 from room where name = 'Paulo Freire');

INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-08 09:00:00', 'empty', 60 from room where name = 'PMPA');
INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-09 09:00:00', 'empty', 60 from room where name = 'PMPA');
INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-10 09:00:00', 'empty', 60 from room where name = 'PMPA');
INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-11 09:00:00', 'empty', 60 from room where name = 'PMPA');

INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-08 09:00:00', 'empty', 60 from room where name = 'Lab. Tec. Livre');
INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-09 09:00:00', 'empty', 60 from room where name = 'Lab. Tec. Livre');
INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-10 09:00:00', 'empty', 60 from room where name = 'Lab. Tec. Livre');
INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-11 09:00:00', 'empty', 60 from room where name = 'Lab. Tec. Livre');

INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-08 09:00:00', 'empty', 60 from room where name = 'Terr. Ap. Livre');
INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-09 09:00:00', 'empty', 60 from room where name = 'Terr. Ap. Livre');
INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-10 09:00:00', 'empty', 60 from room where name = 'Terr. Ap. Livre');
INSERT INTO slot (room_id, blocked, begins, status, duration) (SELECT id, 't', '2015-07-11 09:00:00', 'empty', 60 from room where name = 'Terr. Ap. Livre');

COMMIT;
