begin transaction;

    UPDATE proposal SET track_id = track_id - 24 WHERE track_id >= 129;
    DELETE FROM track WHERE id >= 129;

commit;
