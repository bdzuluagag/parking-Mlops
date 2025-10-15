CREATE OR REPLACE TABLE `pure-heuristic-471315-i8.parking_dataset.parking_features` AS
SELECT
  timestamp,
  parking_id,
  available_spots,
  LAG(available_spots, 1) OVER (
    PARTITION BY parking_id
    ORDER BY timestamp
  ) AS lag_1,
  AVG(available_spots) OVER (
    PARTITION BY parking_id
    ORDER BY timestamp
    ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
  ) AS ma_5
FROM `pure-heuristic-471315-i8.parking_dataset.raw_parking`;
