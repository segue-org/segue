ALTER TYPE product_kinds ADD VALUE 'speaker';
ALTER TYPE product_kinds ADD VALUE 'worker';
ALTER TYPE product_kinds ADD VALUE 'public';

BEGIN TRANSACTION;
    UPDATE product SET kind = 'speaker' WHERE category = 'speaker';
    UPDATE product SET kind = 'public'  WHERE category in (
        'business', 'government',
        'caravan', 'caravan-leader',
        'foreigner', 'foreigner-student',
        'normal', 'student',
        'promocode',
        'proponent', 'proponent-student'
    );
    UPDATE product SET kind = 'worker' WHERE category in (
        'exhibitor', 'organization', 'press', 'service', 'support'
    );

COMMIT;
