CREATE DATABASE movr;


USE movr;


CREATE TABLE users (
      id UUID NOT NULL,
      city STRING NOT NULL,
      first_name STRING NULL,
      last_name STRING NULL,
      address STRING NULL,
      email STRING NULL,
      username STRING NULL,
      password_hash STRING NULL,
      promos_used JSONB NULL, 
      CONSTRAINT "primary" PRIMARY KEY (city ASC, id ASC),
      UNIQUE INDEX users_username_key (username ASC),
      FAMILY "primary" (id, city, first_name, last_name, address, email, username, password_hash, promos_used)
  ) PARTITION BY LIST (city) (
      PARTITION us_west VALUES IN (('seattle'), ('san francisco'), ('los angeles')),
      PARTITION us_east VALUES IN (('new york'), ('boston'), ('washington dc')),
      PARTITION europe_west VALUES IN (('amsterdam'), ('paris'), ('rome'))
  );
  ALTER PARTITION europe_west OF INDEX movr.public.users@primary CONFIGURE ZONE USING
      constraints = '[+region=europe-west1]';
  ALTER PARTITION us_east OF INDEX movr.public.users@primary CONFIGURE ZONE USING
      constraints = '[+region=us-east1]';
  ALTER PARTITION us_west OF INDEX movr.public.users@primary CONFIGURE ZONE USING
      constraints = '[+region=us-west1]'
;

CREATE TABLE vehicles (
      id UUID NOT NULL,
      city STRING NOT NULL,
      type STRING NULL,
      owner_id UUID NULL,
      creation_time TIMESTAMP NULL,
      status STRING NULL,
      last_location STRING NULL,
      color STRING NULL,
      brand STRING NULL,
      CONSTRAINT "primary" PRIMARY KEY (city ASC, id ASC),
      CONSTRAINT fk_city_ref_users FOREIGN KEY (city, owner_id) REFERENCES users(city, id),
      INDEX vehicles_auto_index_fk_city_ref_users (city ASC, owner_id ASC) PARTITION BY LIST (city) (
          PARTITION us_west VALUES IN (('seattle'), ('san francisco'), ('los angeles')),
          PARTITION us_east VALUES IN (('new york'), ('boston'), ('washington dc')),
          PARTITION europe_west VALUES IN (('amsterdam'), ('paris'), ('rome'))
      ),
      FAMILY "primary" (id, city, type, owner_id, creation_time, status, last_location, color, brand)
  ) PARTITION BY LIST (city) (
      PARTITION us_west VALUES IN (('seattle'), ('san francisco'), ('los angeles')),
      PARTITION us_east VALUES IN (('new york'), ('boston'), ('washington dc')),
      PARTITION europe_west VALUES IN (('amsterdam'), ('paris'), ('rome'))
  );
  ALTER PARTITION europe_west OF INDEX movr.public.vehicles@primary CONFIGURE ZONE USING
      constraints = '[+region=europe-west1]';
  ALTER PARTITION us_east OF INDEX movr.public.vehicles@primary CONFIGURE ZONE USING
      constraints = '[+region=us-east1]';
  ALTER PARTITION us_west OF INDEX movr.public.vehicles@primary CONFIGURE ZONE USING
      constraints = '[+region=us-west1]';
  ALTER PARTITION europe_west OF INDEX movr.public.vehicles@vehicles_auto_index_fk_city_ref_users CONFIGURE ZONE USING
      constraints = '[+region=europe-west1]';
  ALTER PARTITION us_east OF INDEX movr.public.vehicles@vehicles_auto_index_fk_city_ref_users CONFIGURE ZONE USING
      constraints = '[+region=us-east1]';
  ALTER PARTITION us_west OF INDEX movr.public.vehicles@vehicles_auto_index_fk_city_ref_users CONFIGURE ZONE USING
      constraints = '[+region=us-west1]'
;

  CREATE TABLE rides (
      id UUID NOT NULL,
      city STRING NOT NULL,
      rider_id UUID NULL,
      vehicle_id UUID NULL,
      vehicle_city STRING NULL,
      start_location STRING NULL,
      end_location STRING NULL,
      start_time TIMESTAMP NULL,
      end_time TIMESTAMP NULL,
      length INTERVAL NULL,
      revenue DECIMAL(10,2) NULL,
      CONSTRAINT "primary" PRIMARY KEY (city ASC, id ASC),
      CONSTRAINT fk_city_ref_users FOREIGN KEY (city, rider_id) REFERENCES users(city, id),
      CONSTRAINT fk_vehicle_city_ref_vehicles FOREIGN KEY (vehicle_city, vehicle_id) REFERENCES vehicles(city, id),
      INDEX rides_auto_index_fk_city_ref_users (city ASC, rider_id ASC) PARTITION BY LIST (city) (
          PARTITION us_west VALUES IN (('seattle'), ('san francisco'), ('los angeles')),
          PARTITION us_east VALUES IN (('new york'), ('boston'), ('washington dc')),
          PARTITION europe_west VALUES IN (('amsterdam'), ('paris'), ('rome'))
      ),
      INDEX rides_auto_index_fk_vehicle_city_ref_vehicles (vehicle_city ASC, vehicle_id ASC) PARTITION BY LIST (vehicle_city) (
          PARTITION us_west VALUES IN (('seattle'), ('san francisco'), ('los angeles')),
          PARTITION us_east VALUES IN (('new york'), ('boston'), ('washington dc')),
          PARTITION europe_west VALUES IN (('amsterdam'), ('paris'), ('rome'))
      ),
      FAMILY "primary" (id, city, rider_id, vehicle_id, vehicle_city, start_location, end_location, start_time, end_time, length, revenue),
      CONSTRAINT check_vehicle_city_city CHECK (vehicle_city = city)
  ) PARTITION BY LIST (city) (
      PARTITION us_west VALUES IN (('seattle'), ('san francisco'), ('los angeles')),
      PARTITION us_east VALUES IN (('new york'), ('boston'), ('washington dc')),
      PARTITION europe_west VALUES IN (('amsterdam'), ('paris'), ('rome'))
  );
  ALTER PARTITION europe_west OF INDEX movr.public.rides@primary CONFIGURE ZONE USING
      constraints = '[+region=europe-west1]';
  ALTER PARTITION us_east OF INDEX movr.public.rides@primary CONFIGURE ZONE USING
      constraints = '[+region=us-east1]';
  ALTER PARTITION us_west OF INDEX movr.public.rides@primary CONFIGURE ZONE USING
      constraints = '[+region=us-west1]';
  ALTER PARTITION europe_west OF INDEX movr.public.rides@rides_auto_index_fk_city_ref_users CONFIGURE ZONE USING
      constraints = '[+region=europe-west1]';
  ALTER PARTITION us_east OF INDEX movr.public.rides@rides_auto_index_fk_city_ref_users CONFIGURE ZONE USING
      constraints = '[+region=us-east1]';
  ALTER PARTITION us_west OF INDEX movr.public.rides@rides_auto_index_fk_city_ref_users CONFIGURE ZONE USING
      constraints = '[+region=us-west1]';
  ALTER PARTITION europe_west OF INDEX movr.public.rides@rides_auto_index_fk_vehicle_city_ref_vehicles CONFIGURE ZONE USING
      constraints = '[+region=europe-west1]';
  ALTER PARTITION us_east OF INDEX movr.public.rides@rides_auto_index_fk_vehicle_city_ref_vehicles CONFIGURE ZONE USING
      constraints = '[+region=us-east1]';
  ALTER PARTITION us_west OF INDEX movr.public.rides@rides_auto_index_fk_vehicle_city_ref_vehicles CONFIGURE ZONE USING
      constraints = '[+region=us-west1]'
;


  CREATE TABLE promo_codes (
      id UUID NOT NULL,
      code STRING NOT NULL UNIQUE,
      description STRING NULL,
      creation_time TIMESTAMP NULL,
      expiration_time TIMESTAMP NULL,
      percent_off INT NULL,
      CONSTRAINT "primary" PRIMARY KEY (id ASC, code ASC),
      CONSTRAINT is_percent CHECK (percent_off BETWEEN 0 AND 100),
      FAMILY "primary" (id, code, description, creation_time, expiration_time, percent_off)
  );

