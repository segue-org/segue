BEGIN TRANSACTION;
    INSERT INTO room (position, name, capacity, translation)
    VALUES
        (9,  '712 - OF1',       40, 'f'),
        (10, '713 Mozilla',     40, 'f'),
        (11, '714',             70, 'f'),
        (12, '715',             70, 'f'),
        (13, 'Paulo Freire',    20, 'f'),
        (14, 'PMPA',            20, 'f'),
        (15, 'Lab. Tec. Livre', 20, 'f'),
        (16, 'Terr. Ap. Livre', 20, 'f'),
        (17, 'Hackaton Robot.', 20, 'f');

COMMIT;
