DAG_ID = "GEO_INGEST"

DAG_PARAMS = {}

DAG_TAGS = ["GEO_INGEST", ]

MINUTES_TIMEDELTA = 10

STATION_UPSERT_SQL = """
                     INSERT INTO stations (station_id, station_name_en, station_name_gr, latitude, longitude, elevation,
                                           first_seen, last_seen)
                     VALUES (%(station_id)s, %(station_name_en)s, %(station_name_gr)s, %(latitude)s, %(longitude)s,
                             %(elevation)s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                     ON CONFLICT (station_id) DO UPDATE SET station_name_en = EXCLUDED.station_name_en,
                                                            station_name_gr = EXCLUDED.station_name_gr,
                                                            latitude        = EXCLUDED.latitude,
                                                            longitude       = EXCLUDED.longitude,
                                                            elevation       = EXCLUDED.elevation,
                                                            last_seen       = CURRENT_TIMESTAMP; \
                     """

OBS_UPSERT_SQL = """
                 INSERT INTO observations (time, station_id, temp_out, hi_temp, low_temp, out_hum,
                                           bar, rain, wind_speed, wind_dir, wind_dir_str,
                                           hi_speed, hi_dir, hi_dir_str)
                 VALUES (%(time)s,
                         %(station_id)s,
                         %(temp_out)s,
                         %(hi_temp)s,
                         %(low_temp)s,
                         %(out_hum)s,
                         %(bar)s,
                         %(rain)s,
                         %(wind_speed)s,
                         %(wind_dir)s,
                         %(wind_dir_str)s,
                         %(hi_speed)s,
                         %(hi_dir)s,
                         %(hi_dir_str)s)
                 ON CONFLICT DO NOTHING; \
                 """
