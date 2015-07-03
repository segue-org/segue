begin transaction;
    update product set can_pay_cash = 't', sold_until = '2015-07-11 23:59:59' where category like 'proponent%';
commit;
