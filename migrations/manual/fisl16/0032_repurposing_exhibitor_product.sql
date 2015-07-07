BEGIN TRANSACTION;

    UPDATE product SET kind = 'public',
                       category = 'sponsor',
                       description = 'patrocinador'
                 WHERE category = 'exhibitor';

COMMIT;
