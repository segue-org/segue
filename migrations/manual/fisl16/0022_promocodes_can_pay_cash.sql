BEGIN TRANSACTION;
    UPDATE product SET can_pay_cash = 't' WHERE is_promo = 't';
COMMIT;
