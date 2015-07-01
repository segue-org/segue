BEGIN TRANSACTION;
    UPDATE product SET category = 'promocode' WHERE is_promo = 't';
COMMIT;
