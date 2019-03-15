use test
set names utf8;

-- 1. Выбрать все товары (все поля)
SELECT * FROM product;

-- 2. Выбрать названия всех автоматизированных складов
SELECT name FROM store;

-- 3. Посчитать общую сумму в деньгах всех продаж
SELECT sum(total) FROM sale;

-- 4. Получить уникальные store_id всех складов, с которых была хоть одна продажа
SELECT DISTINCT store_id FROM store INNER JOIN sale USING(store_id);

-- 5. Получить уникальные store_id всех складов, с которых не было ни одной продажи
SELECT DISTINCT store_id FROM store LEFT JOIN sale USING(store_id) WHERE sale_id IS NULL;

-- 6. Получить для каждого товара название и среднюю стоимость единицы товара avg(total/quantity), если товар не продавался, он не попадает в отчет.
SELECT name, avg(total/quantity) FROM product INNER JOIN sale USING(product_id) GROUP BY name;

-- 7. Получить названия всех продуктов, которые продавались только с единственного склада
SELECT product.name FROM store INNER JOIN sale USING(store_id) INNER JOIN product USING(product_id) GROUP BY product.name HAVING COUNT(DISTINCT store.name)=1;

-- 8. Получить названия всех складов, с которых продавался только один продукт
SELECT store.name FROM store INNER JOIN sale USING(store_id) GROUP BY store.name HAVING COUNT(DISTINCT product_id)=1;

-- 9. Выберите все ряды (все поля) из продаж, в которых сумма продажи (total) максимальна (равна максимальной из всех встречающихся)
SELECT * FROM sale WHERE total=(SELECT max(total) FROM sale);

-- 10. Выведите дату самых максимальных продаж, если таких дат несколько, то самую раннюю из них
SELECT min(date) from sale where total=(select max(total) from sale);
