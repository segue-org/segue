BEGIN TRANSACTION;

INSERT INTO track (name_pt, name_en, public)
    VALUES ('Oficinas - Oficinas',                        'Workshops - Workshops',             'f'),
           (E'T\u00F3picos Emergentes - Cloud Computing', 'Trending Topics - Cloud Computing', 'f');

COMMIT;
