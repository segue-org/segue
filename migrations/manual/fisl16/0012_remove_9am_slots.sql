begin transaction;
    DELETE FROM slot WHERE extract(hour from begins) = 9;
commit;
