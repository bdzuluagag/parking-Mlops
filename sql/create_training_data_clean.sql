CREATE OR REPLACE TABLE `pure-heuristic-471315-i8.parking_dataset.training_data_clean` AS
SELECT *
FROM `pure-heuristic-471315-i8.parking_dataset.training_data`
WHERE target_t_plus_10 IS NOT NULL;
