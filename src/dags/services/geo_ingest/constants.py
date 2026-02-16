from datetime import date
from airflow.sdk import Param

DAG_ID = "GEO_INGEST"

DAG_PARAMS = {
}

DAG_TAGS = ["GEO_INGEST", ]


STATION_UPSERT_SQL = """
INSERT INTO stations (
  station_id,
  station_file,
  station_name_gr,
  station_name_en,
  longitude,
  latitude,
  elevation_m,
  updated_at
)
VALUES (
  %(station_id)s,
  %(station_file)s,
  %(station_name_gr)s,
  %(station_name_en)s,
  %(longitude)s,
  %(latitude)s,
  %(elevation_m)s,
  now()
)
ON CONFLICT (station_id) DO UPDATE
SET
  station_file    = EXCLUDED.station_file,
  station_name_gr = EXCLUDED.station_name_gr,
  station_name_en = EXCLUDED.station_name_en,
  longitude       = EXCLUDED.longitude,
  latitude        = EXCLUDED.latitude,
  elevation_m     = EXCLUDED.elevation_m,
  updated_at      = now();
"""

OBS_UPSERT_SQL = """
INSERT INTO observations (
  time,
  station_id,

  temp_out_c,
  hi_temp_c,
  low_temp_c,
  out_hum_pct,
  bar_hpa,
  rain_mm,

  wind_speed_ms,
  wind_dir_deg,
  wind_dir_str,

  hi_speed_ms,
  hi_dir_deg,
  hi_dir_str,

  source_ts,
  source_date_text,
  ingested_at
)
VALUES (
  %(time)s,
  %(station_id)s,

  %(temp_out_c)s,
  %(hi_temp_c)s,
  %(low_temp_c)s,
  %(out_hum_pct)s,
  %(bar_hpa)s,
  %(rain_mm)s,

  %(wind_speed_ms)s,
  %(wind_dir_deg)s,
  %(wind_dir_str)s,

  %(hi_speed_ms)s,
  %(hi_dir_deg)s,
  %(hi_dir_str)s,

  %(source_ts)s,
  %(source_date_text)s,
  now()
)
ON CONFLICT (time, station_id) DO UPDATE
SET
  temp_out_c       = EXCLUDED.temp_out_c,
  hi_temp_c        = EXCLUDED.hi_temp_c,
  low_temp_c       = EXCLUDED.low_temp_c,
  out_hum_pct      = EXCLUDED.out_hum_pct,
  bar_hpa          = EXCLUDED.bar_hpa,
  rain_mm          = EXCLUDED.rain_mm,

  wind_speed_ms    = EXCLUDED.wind_speed_ms,
  wind_dir_deg     = EXCLUDED.wind_dir_deg,
  wind_dir_str     = EXCLUDED.wind_dir_str,

  hi_speed_ms      = EXCLUDED.hi_speed_ms,
  hi_dir_deg       = EXCLUDED.hi_dir_deg,
  hi_dir_str       = EXCLUDED.hi_dir_str,

  source_ts        = EXCLUDED.source_ts,
  source_date_text = EXCLUDED.source_date_text,
  ingested_at      = now();
"""